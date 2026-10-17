"""Generate a standalone project without copying Git history or build output."""

import argparse
from pathlib import Path
import re
import shutil
import tempfile


PROJECT_LINE = re.compile(
    r"(?m)^project\([A-Za-z][A-Za-z0-9_]* VERSION ([0-9]+\.[0-9]+\.[0-9]+) LANGUAGES CXX\)$"
)
DIRECTORIES = ("cmake", "include", "source", "tests", "scripts", ".githooks", "docs")
FILES = ("CMakeLists.txt", "CMakePresets.json", ".gitignore", ".gitattributes", "README.md", "AGENTS.md",
         ".clang-tidy", "uncrustify.cfg")


def generate(name: str, parent: Path, template: Path) -> Path:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
        raise ValueError("Name must start with a letter and contain only ASCII letters, digits or underscores")
    parent = parent.resolve()
    template = template.resolve()
    if not parent.is_dir():
        raise ValueError(f"Parent directory does not exist: {parent}")
    target = parent / name
    if target.exists():
        raise FileExistsError(f"Destination already exists: {target}")

    # Stage beside the destination; publish only a complete generated project.
    with tempfile.TemporaryDirectory(prefix=".cpp-template-", dir=parent) as temporary:
        staging = Path(temporary) / name
        staging.mkdir()
        for directory in DIRECTORIES:
            shutil.copytree(
                template / directory, staging / directory,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        for filename in FILES:
            shutil.copyfile(template / filename, staging / filename)
        cmake_file = staging / "CMakeLists.txt"
        content, replacements = PROJECT_LINE.subn(
            lambda match: f"project({name} VERSION {match.group(1)} LANGUAGES CXX)",
            cmake_file.read_text(encoding="utf-8"),
        )
        if replacements != 1:
            raise ValueError("Expected one project(NAME VERSION x.y.z LANGUAGES CXX) declaration")
        cmake_file.write_text(content, encoding="utf-8", newline="\n")
        staging.rename(target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--path", required=True, type=Path, help="Existing parent directory")
    args = parser.parse_args()
    try:
        target = generate(args.name, args.path, Path(__file__).resolve().parents[1])
    except (OSError, ValueError) as error:
        parser.exit(1, f"Generation failed: {error}\n")
    print(f"Created: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
