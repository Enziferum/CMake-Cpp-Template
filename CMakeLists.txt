cmake_minimum_required(VERSION 3.24)
project(cmake_cpp_template VERSION 0.1.0 LANGUAGES CXX)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "Use an out-of-source build: cmake -S . -B build/debug")
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_CONFIGURATION_TYPES AND NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build configuration" FORCE)
endif()

include(CTest)
include(cmake/CompilerOptions.cmake)
include(cmake/Dependencies.cmake)

configure_file(cmake/Version.hpp.in generated/app/Version.hpp @ONLY)

add_library(${PROJECT_NAME}-core STATIC source/Logger.cpp)
target_include_directories(${PROJECT_NAME}-core PUBLIC
    "${PROJECT_SOURCE_DIR}/include"
    "${PROJECT_BINARY_DIR}/generated")
target_link_libraries(${PROJECT_NAME}-core PUBLIC spdlog::spdlog)
configure_project_warnings(${PROJECT_NAME}-core)

add_executable(${PROJECT_NAME}-exe source/main.cpp)
target_link_libraries(${PROJECT_NAME}-exe PRIVATE ${PROJECT_NAME}-core)
configure_project_warnings(${PROJECT_NAME}-exe)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
