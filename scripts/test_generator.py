from pathlib import Path
import tempfile
import unittest

from gen_project import generate


class GeneratorTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.template = Path(__file__).resolve().parents[1]

    def test_generates_standalone_project(self):
        target = generate("ExampleApp", self.parent, self.template)
        cmake = (target / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("project(ExampleApp VERSION ", cmake)
        self.assertNotIn("project(cmake_cpp_template ", cmake)
        for relative in (".gitignore", "AGENTS.md", "include/app/Logger.hpp", "scripts/gen_project.py",
                         ".clang-tidy", "uncrustify.cfg", ".githooks/pre-commit",
                         "scripts/install_git_hooks.py", "docs/development-tools.md"):
            self.assertTrue((target / relative).is_file(), relative)
        self.assertFalse((target / ".git").exists())
        self.assertFalse((target / "build").exists())
        # A generated project is itself still a usable template.
        second = generate("SecondApp", self.parent, target)
        self.assertIn("project(SecondApp VERSION ", (second / "CMakeLists.txt").read_text(encoding="utf-8"))

    def test_refuses_to_overwrite_destination(self):
        target = self.parent / "Existing"
        target.mkdir()
        sentinel = target / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            generate("Existing", self.parent, self.template)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_rejects_unsafe_names(self):
        for name in ("../escape", "a/b", "a-b", "9app", "", "CMake;bad"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                generate(name, self.parent, self.template)

    def test_failure_does_not_publish_partial_project(self):
        empty_template = self.parent / "empty"
        empty_template.mkdir()
        with self.assertRaises(OSError):
            generate("Incomplete", self.parent, empty_template)
        self.assertFalse((self.parent / "Incomplete").exists())
        self.assertEqual(sorted(path.name for path in self.parent.iterdir()), ["empty"])


if __name__ == "__main__":
    unittest.main()
