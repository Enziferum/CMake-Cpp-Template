#include <iostream>
#include <algorithm>
#include <cstdint>
#include <vector>
#include <unordered_map>

class Argument {
public:
    enum class Type {
        Positional,
        Optional
    };
public:
    Argument() = default;
    Argument(Type type);
    Argument(const Argument& other) = default;
    Argument& operator=(const Argument& other) = default;
    Argument(Argument&& other) = default;
    Argument& operator=(Argument&& other) = default;
    ~Argument() = default;

    Argument& help(const std::string& help) {
        m_help = help;
        return *this;
    }

    bool is_positional() const { return m_type == Type::Positional;}
    bool is_optional() const { return m_type == Type::Optional;}
    bool is_required() const { return m_required; }
private:
    std::string m_help;
    Type m_type;
    bool m_required{ false };
};

Argument::Argument(Argument::Type type):
    m_type(type) {}

// \brief Simple argument parser for base purposes. if you need something more complex
// you can use for example ... .
class SimpleArgumentParser {
public:
    SimpleArgumentParser(const std::string& name);
    SimpleArgumentParser(const SimpleArgumentParser& other) = delete;
    SimpleArgumentParser& operator=(const SimpleArgumentParser& other) = delete;
    SimpleArgumentParser(SimpleArgumentParser&& other) = delete;
    SimpleArgumentParser& operator=(SimpleArgumentParser&& other) = delete;
    ~SimpleArgumentParser() = default;

    Argument& add_argument(const std::string& name);
    Argument& add_argument(const std::string& shortArg, const std::string& longArg);


    Argument& operator[](const std::string& name) {
        return m_arguments[m_rawArguments.at(name)];
    }

    const Argument& operator[](const std::string& name) const {
        return m_arguments.at(m_rawArguments.at(name));
    }

    bool parse_args(int argc, char** argv);
private:
    void printHelp();

private:
    using ArgumentID = std::uint32_t;

    ArgumentID m_current = 0;
    std::string m_name;

    std::unordered_map<std::string, ArgumentID> m_rawArguments;
    std::unordered_map<ArgumentID, Argument> m_arguments;
};

SimpleArgumentParser::SimpleArgumentParser(const std::string& name): m_name{name} {}

void SimpleArgumentParser::printHelp() {

}


Argument& SimpleArgumentParser::add_argument(const std::string& name) {
    Argument::Type argType{};
    if(name[0] == '-') {
        argType = Argument::Type::Optional;
    }
    else {
        argType = Argument::Type::Positional;
    }


    Argument arg{argType};
    return arg;
}

Argument& SimpleArgumentParser::add_argument(const std::string& shortArg, const std::string& longArg) {
    Argument::Type argType = Argument::Type::Optional;

    Argument arg{argType};
    return arg;
}


bool SimpleArgumentParser::parse_args(int argc, char** argv) {
    if(argc == 1) {

        return false;
    }

    auto removeWhiteSpaces = [](std::string& str) {
      	str.erase(std::remove_if(str.begin(), str.end(), isspace), str.end());
    };

    /// cat cat.c -n
    /// cat -n cat.c
    /// cat cat.c -n 10


    bool isProcessingOptionalArgument = false; // -v --verbose
    for(int i = 1; i < argc; ++i) {
        std::string current = argv[i];

        if(current.empty())
            continue;
        if(current[0] == '-') {
            if(current.size() == 1) {
                // TODO(a.raag): think what todo
            }
            else {
                if(current[1] == '-') {
                    isProcessingOptionalArgument = true;
                    removeWhiteSpaces(current);

                }
                else if(std::isdigit(current[1])) {
                    // negative value
                    removeWhiteSpaces(current);
                    int value = std::stoi(current);

                }
                else if(std::isalpha(current[1])) {
                    isProcessingOptionalArgument = true;
                    removeWhiteSpaces(current);

                }
                else {
                    /// not
                }
            }
        }
        else {

        }

    }

    return true;
}


int main(int argc, char** argv) {
    SimpleArgumentParser argumentParser{"test"};

    try {
        argumentParser.
            add_argument("sum").
            help("");

        argumentParser.parse_args(argc, argv);
    }
    catch(const std::exception& exception) {
        std::cerr << exception.what() << std::endl;
    }

    return 0;
}
