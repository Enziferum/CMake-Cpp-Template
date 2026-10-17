"""Enable the repository's versioned hooks for this checkout."""

from pathlib import Path
import argparse
import subprocess
import sys

import pre_commit as hook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uncrustify", default="uncrustify", help="Uncrustify 0.83.0 executable")
    parser.add_argument("--clang-tidy", default="clang-tidy")
    parser.add_argument("--powershell", default="pwsh", help="PowerShell 7 executable")
    parser.add_argument("--build-dir", default="work/pre-commit-build")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    root = Path(__file__).resolve().parents[1]
    try:
        # Validate tools before changing Git configuration.
        hook.validate_build_directory(args.build_dir)
        formatter = hook.executable(args.uncrustify)
        if "Uncrustify-0.83.0" not in hook.execute([formatter, "--version"], capture=True):
            raise hook.CheckError("Uncrustify 0.83.0 is required")
        tidy = hook.executable(args.clang_tidy)
        powershell = hook.executable(args.powershell)
        for name in ("cmake", "ninja", "ctest"):
            hook.executable(name)
        current = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=root,
                                 capture_output=True, text=True)
        if current.returncode not in (0, 1):
            raise hook.CheckError(current.stderr.strip())
        if current.stdout.strip() not in ("", ".githooks"):
            raise hook.CheckError("Existing core.hooksPath was preserved; integrate hooks manually")
        if not current.stdout.strip():
            default = Path(hook.execute(["git", "rev-parse", "--git-path", "hooks/pre-commit"], capture=True).strip())
            if not default.is_absolute():
                default = root / default
            if default.exists():
                raise hook.CheckError("Existing pre-commit hook was preserved; integrate hooks manually")
        file = root / ".githooks/pre-commit"
        file.chmod(file.stat().st_mode | 0o111)
        settings = {"uncrustify": formatter, "clangTidy": tidy, "powershell": powershell,
                    "python": sys.executable, "buildDirectory": args.build_dir, "jobs": str(args.jobs)}
        for name, value in settings.items():
            hook.execute(["git", "config", "--local", f"cppTemplate.hooks.{name}", value])
        hook.execute(["git", "config", "--local", "core.hooksPath", ".githooks"])
    except (hook.CheckError, OSError, ValueError) as error:
        print(f"Hook installation failed: {error}", file=sys.stderr)
        return 1
    print("Enabled pre-commit: format, build, tests and strict clang-tidy. Sources and index unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
