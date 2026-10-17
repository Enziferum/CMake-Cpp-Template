# C++ project instructions

- C++20, CMake 3.24+, Ninja; Windows builds prefer MinGW64. Add GUI dependencies only when required.
- Read README.md and docs/development-tools.md for build and tool commands.
- Keep the version only in the root project(... VERSION ...). Do not edit generated app/Version.hpp.
- Add reusable sources explicitly to ${PROJECT_NAME}-core; the application and tests link that target.
- Use app::Logger for application logging. Pass runtime text to write() or as a "{}" argument.
- Style: 4 spaces, namespace indentation, same-line braces, T*/T& beside the type, if(...), object -> method(). Preserve include order.
- Use Uncrustify 0.83.0 with uncrustify.cfg, not clang-format. Formatting is an explicit operation.
- Install .githooks with scripts/install_git_hooks.py before committing. Do not bypass failed checks.
- Pre-commit checks format, a dedicated Release build, tests and strict clang-tidy. Keep check inputs consistent with the Git index; do not rewrite or stash user changes.
- Limit normal analysis to include/, source/ and tests/. Do not apply project warnings or formatting to dependencies.
- After behavioral changes run relevant tests. After generator changes also verify a generated project with a different name.
- Keep machine paths, credentials, internal notes, logs and backups outside versioned content; local builds and working materials belong in ignored work/ or build/.
