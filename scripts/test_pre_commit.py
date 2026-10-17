"""Regression checks for hook scope, staging safety and failure propagation."""

import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import pre_commit as hook


class PreCommitTests(unittest.TestCase):
    def test_configuration_and_templates_trigger_native_checks(self):
        for path in ("cmake/Version.hpp.in", "include/app/BuildInfo.hpp.in", "CMakePresets.json",
                     ".clang-tidy", "uncrustify.cfg", "scripts/run_clang_tidy.ps1"):
            with self.subTest(path=path), patch("sys.stdout", new_callable=io.StringIO) as output:
                hook.check([path], plan=True)
                self.assertTrue(json.loads(output.getvalue())["native_build_and_tests"])

    def test_documentation_and_dependencies_do_not_invoke_tools(self):
        for path in ("README.md", "docs/development-tools.md", "extlibs/lib/a.cpp",
                     "build/_deps/lib/source/a.cpp", "work/probe.cpp", "source-backup/a.cpp"):
            with self.subTest(path=path), patch.object(hook, "execute") as run:
                hook.check([path])
                run.assert_not_called()

    def test_deleted_source_still_triggers_build(self):
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            hook.check(["source/deleted.cpp"], plan=True)
            plan = json.loads(output.getvalue())
            self.assertTrue(plan["native_build_and_tests"])
            self.assertEqual(plan["format"], [])

    def test_python_changes_only_run_regressions(self):
        with patch.object(hook, "execute") as run, patch.object(hook, "git_paths", return_value=[]), \
                patch.object(hook, "executable") as tool:
            hook.check(["scripts/pre_commit.py"])
            self.assertIn("unittest", run.call_args.args[0])
            tool.assert_not_called()

    def test_partial_staging_and_untracked_inputs_block_before_checks(self):
        for unstaged, untracked in ((["include/app/Logger.hpp"], []), ([], ["source/Untracked.cpp"]),
                                   (["scripts/pre_commit.py"], []), (["CMakePresets.json"], [])):
            with self.subTest(unstaged=unstaged, untracked=untracked), \
                    patch.object(hook, "execute") as run, \
                    patch.object(hook, "git_paths", side_effect=[unstaged, untracked]):
                with self.assertRaisesRegex(hook.CheckError, "Stage or set aside"):
                    hook.check(["source/main.cpp"])
                run.assert_not_called()

    def test_command_failure_is_not_success(self):
        with patch.object(hook.subprocess, "run", return_value=subprocess.CompletedProcess(
                ["tool"], 1, stdout="", stderr="diagnostic")):
            with self.assertRaisesRegex(hook.CheckError, "diagnostic"):
                hook.execute(["tool"], capture=True)

    def test_dependency_mapping_only_selects_affected_units(self):
        root = hook.ROOT
        a, b = root / "source/A.cpp", root / "source/B.cpp"
        header = root / "include/app/A.hpp"
        entries = [{"file": str(path), "directory": str(root)} for path in (a, b)]
        dependencies = f"a.o: #deps 2\n    {a}\n    {header}\n\nb.o: #deps 1\n    {b}\n"
        self.assertEqual(hook.affected_units(["include/app/A.hpp"], entries, dependencies, root),
                         [hook.normal(a)])

    def test_uncompiled_header_is_rejected(self):
        with self.assertRaisesRegex(hook.CheckError, "No compilation/dependency coverage"):
            hook.affected_units(["include/app/Unused.hpp"], [], "", hook.ROOT)

    def test_compile_database_excludes_dependencies_and_outside_files(self):
        paths = (hook.ROOT / "source/main.cpp", hook.ROOT / "build/_deps/lib/a.cpp",
                 hook.ROOT.parent / "other.cpp")
        entries = [{"directory": str(hook.ROOT), "file": str(path)} for path in paths]
        self.assertEqual(hook.own_entries(entries), entries[:1])

    def test_formatter_failure_stops_before_build_without_rewriting(self):
        commands = []

        def run(command, **kwargs):
            commands.append([str(value) for value in command])
            if "--version" in command:
                return "Uncrustify-0.83.0_f"
            if "--check" in command:
                raise hook.CheckError("format mismatch")
            return ""

        with patch.object(hook, "execute", side_effect=run), \
                patch.object(hook, "git_paths", return_value=[]), \
                patch.object(hook, "option", side_effect=lambda name, default: default), \
                patch.object(hook, "executable", side_effect=lambda name: name):
            with self.assertRaisesRegex(hook.CheckError, "format mismatch"):
                hook.check(["source/main.cpp"])
        self.assertFalse(any("--replace" in cmd or "--build" in cmd or "add" in cmd for cmd in commands))

    def test_build_directory_must_be_dedicated(self):
        for value in (".", "work", "build/debug", "../other"):
            with self.subTest(value=value), self.assertRaises(hook.CheckError):
                hook.validate_build_directory(value)
        self.assertEqual(hook.validate_build_directory("work/hook"), (hook.ROOT / "work/hook").resolve())

    def test_existing_ide_cache_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            build = root / "work/hook"
            build.mkdir(parents=True)
            (build / "CMakeCache.txt").write_text("CMAKE_GENERATOR:INTERNAL=Ninja\nCMAKE_BUILD_TYPE:STRING=Debug\n")
            with patch.object(hook, "ROOT", root), self.assertRaises(hook.CheckError):
                hook.validate_build_directory("work/hook")

    def test_native_pipeline_propagates_failures(self):
        for failure in (None, "build", "ctest", "tidy"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                source = root / "source/Probe.cpp"
                source.parent.mkdir(parents=True)
                original = "int probe() { return 0; }\n"
                source.write_text(original)
                build = root / "work/pre-commit-build"
                build.mkdir(parents=True)
                (build / "compile_commands.json").write_text(json.dumps([
                    {"file": str(source), "directory": str(root)}]))
                commands = []

                def run(command, **kwargs):
                    command = [str(value) for value in command]
                    commands.append(command)
                    if "--version" in command:
                        return "Uncrustify-0.83.0_f"
                    if "-t" in command:
                        return f"probe.o: #deps 1\n    {source}\n"
                    stage = ("build" if "--build" in command else "ctest" if command[0] == "ctest"
                             else "tidy" if "-FilesFrom" in command else None)
                    if stage == failure and failure is not None:
                        raise hook.CheckError(f"{stage} failed")
                    return ""

                with patch.object(hook, "ROOT", root), patch.object(hook, "execute", side_effect=run), \
                        patch.object(hook, "git_paths", return_value=[]), \
                        patch.object(hook, "option", side_effect=lambda name, default: default), \
                        patch.object(hook, "executable", side_effect=lambda value: value):
                    if failure:
                        with self.assertRaisesRegex(hook.CheckError, f"{failure} failed"):
                            hook.check(["source/Probe.cpp"])
                    else:
                        hook.check(["source/Probe.cpp"])
                        self.assertIn("-WarningsAsErrors", commands[-1])
                self.assertEqual(source.read_text(), original)
                if failure == "build":
                    self.assertFalse(any(cmd[0] == "ctest" for cmd in commands))
                if failure == "ctest":
                    self.assertFalse(any("-FilesFrom" in cmd for cmd in commands))


if __name__ == "__main__":
    unittest.main()
