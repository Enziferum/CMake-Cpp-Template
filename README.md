# CMake C++ Template

Болванка C++20-проекта: библиотека собственного кода, консольный пример,
версия из CMake, логирование spdlog и тесты GoogleTest/CTest.
Qt и другие GUI-библиотеки добавляются по требованиям конкретного проекта.

## Требования и сборка

CMake 3.24+, C++20-компилятор, Ninja. Для Windows предпочтителен MinGW64.
Python 3.10+ нужен для генератора проектов и его тестов, но не для сборки C++.
Запускайте команды в окружении выбранного toolchain: для MinGW64 каталог
его bin должен быть в PATH перед другими компиляторами и несовместимыми DLL.
Пресеты не меняют глобальный PATH и не фиксируют локальный путь к компилятору.

```text
cmake --preset debug
cmake --build --preset debug -j 4
ctest --preset debug
cmake --preset release
cmake --build --preset release -j 4
```

Первичная конфигурация скачивает spdlog 1.17.0 и, при BUILD_TESTING=ON,
GoogleTest 1.18.0. Версии и SHA-256 архивов закреплены в cmake/Dependencies.cmake.
Тесты и примеры сторонних библиотек отключены. Для сборки без тестов:

```text
cmake -S . -B build/no-tests -G Ninja -DBUILD_TESTING=OFF
cmake --build build/no-tests
```

Для работы без сети заранее подготовьте исходники зависимостей и задайте
FETCHCONTENT_SOURCE_DIR_SPDLOG и FETCHCONTENT_SOURCE_DIR_GOOGLETEST.
Сторонние исходники и сборки не копируются генератором и не хранятся в Git.

## Новый проект

Из корня шаблона, с существующей родительской папкой (например, ../projects):

```text
python scripts/gen_project.py --name ExampleApp --path ../projects
```

Генератор создаёт новую папку ExampleApp, задаёт имя в project() и копирует
только нужные исходники, настройки, инструкции и тесты. Существующую папку
не перезаписывает, Git-историю не переносит, ошибки не скрывает.
Имя начинается с ASCII-буквы и содержит буквы, цифры или подчёркивания.
Namespace app и пути include/app остаются общими; цели получают имя проекта:
ExampleApp-core, ExampleApp-exe и ExampleApp-tests.

## Версия

Единственный источник — project(... VERSION 0.1.0 LANGUAGES CXX) в корне.
Меняйте номер там. configure_file создаёт build/.../generated/app/Version.hpp
с constexpr-полями major, minor, patch, string и projectName.
Приложение показывает версию по --version.
Git SHA, prerelease-суффиксы и Windows VERSIONINFO пока не добавлены.

## Код и тесты

- include/app — публичные заголовки собственного кода.
- source/Logger.cpp и новые исходники библиотеки — цель <project>-core.
- source/main.cpp — только точка входа, цель <project>-exe.
- tests — тесты библиотеки с точкой входа GoogleTest.
- cmake — зависимости, предупреждения и шаблон заголовка версии.

Добавляйте исходники явно в CMakeLists.txt. GoogleTest предоставляет main,
gtest_discover_tests регистрирует отдельные тесты в CTest.
Предупреждения применяются к собственным целям. build/ игнорируется Git.

## Логирование

```cpp
app::LoggerConfig config;
config.level = app::LogLevel::Debug;
config.filePath = "logs/application.log"; // пустой путь отключает файл
app::Logger logger{"application", config};
logger.info("Loaded {} records", 42);
logger.warning("Missing metadata: {}", "track.mp3");
logger.setLevel(app::LogLevel::Error);
logger.write(app::LogLevel::Error, "Runtime text with {braces}");
logger.flush();
```

Уровни: Trace, Debug, Info, Warning, Error, Critical, Off. По умолчанию — Info
и цветная консоль. Файл включается отдельно; ротация по умолчанию — 5 MiB
и до трёх архивов плюс текущий файл. На Windows поддержаны Unicode-пути файлов.
Формат содержит время, имя логгера, уровень и ID потока.

Логгер синхронный, использует sinks с синхронизацией, не регистрирует себя
глобально и не вызывает глобальный shutdown spdlog. Разные экземпляры могут
иметь одинаковые имена. Одновременное использование одного файла разными
экземплярами или процессами не предусмотрено. Завершите использующие логгер
потоки до его уничтожения. Настройка sinks после создания не предоставлена.
Ошибки инициализации передаются исключением; ошибки записи spdlog обрабатывает
своим стандартным обработчиком. Файл может открываться в режиме добавления.

## Проверка генератора

```text
python scripts/test_generator.py
```

Тест также регистрируется в CTest при обнаружении Python.
После изменения шаблона проверьте сборку созданного проекта с другим именем.

## Форматирование и pre-commit

Включены Uncrustify 0.83.0 со стилем проекта, clang-tidy и versioned
pre-commit. После git init установите hooks через scripts/install_git_hooks.py.
Проверки: формат → сборка → тесты → строгий анализ; ошибки блокируют commit.
Источники и индекс hook не переписывает. Пути инструментов — локальные настройки.
Полные команды и требования: [docs/development-tools.md](docs/development-tools.md).
Генератор переносит configs, docs и .githooks в новые проекты.
