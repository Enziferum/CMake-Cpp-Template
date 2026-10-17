add_executable(${PROJECT_NAME}-tests LoggerTests.cpp VersionTests.cpp)
target_link_libraries(${PROJECT_NAME}-tests PRIVATE
    ${PROJECT_NAME}-core GTest::gtest_main)
configure_project_warnings(${PROJECT_NAME}-tests)

include(GoogleTest)
gtest_discover_tests(${PROJECT_NAME}-tests DISCOVERY_MODE PRE_TEST)
add_test(NAME app.version COMMAND $<TARGET_FILE:${PROJECT_NAME}-exe> --version)
set_tests_properties(app.version PROPERTIES
    PASS_REGULAR_EXPRESSION "${PROJECT_NAME} ${PROJECT_VERSION}")

find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
    add_test(NAME generator
        COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/scripts/test_generator.py")
    add_test(NAME tooling
        COMMAND "${Python3_EXECUTABLE}" -m unittest discover
        -s "${PROJECT_SOURCE_DIR}/scripts" -p "test_*commit*.py" -v)
endif()
