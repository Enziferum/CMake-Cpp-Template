cmake_minimum_required(VERSION 3.21)
project(cmake_cpp_template)

if(MSVC)
    add_definitions(/MP)
endif()

if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
    message(FATAL_ERROR "In-source builds not allowed.
    Please make a new directory (called a build directory)
	and run CMake from there. You may need to remove CMakeCache.txt.")
endif()

cmake_policy(SET CMP0074 NEW)

set(CMAKE_CXX_STANDARD 20)
include(cmake/Base.cmake)

file(GLOB_RECURSE INCL include/*.hpp)
file(GLOB_RECURSE SRC source/*.cpp)

list(FILTER SRC EXCLUDE REGEX "source/.*main\\.cpp$")
#add_library(${PROJECT_NAME} ${SRC})
add_executable(${PROJECT_NAME}-exe source/main.cpp)
target_link_libraries(${PROJECT_NAME}-exe PRIVATE ${LIBS})

target_include_directories(${PROJECT_NAME}-exe PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>")

if(BUILD_TESTS)
    add_subdirectory(tests)
endif ()