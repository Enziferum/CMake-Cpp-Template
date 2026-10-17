#include <app/Logger.hpp>
#include <app/Version.hpp>

#include <exception>
#include <iostream>
#include <string_view>

int main(int argc, char** argv) {
    try {
        if(argc == 2 && std::string_view(argv[1]) == "--version") {
            std::cout << app::version::projectName << ' ' << app::version::string << '\n';
            return 0;
        }

        app::Logger logger{std::string(app::version::projectName)};
        logger.info("Starting {} {}", app::version::projectName, app::version::string);
        logger.flush();
        return 0;
    }
    catch(const std::exception& error) {
        std::cerr << "Startup failed: " << error.what() << '\n';
        return 1;
    }
}
