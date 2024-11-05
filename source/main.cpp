#include <iostream>

int main(int argc, char** argv) {
    try {
        std::cout << "Hello, World!" << std::endl;
    }
    catch(const std::exception& exception) {
        std::cerr << exception.what() << std::endl;
    }

    return 0;
}
