#include <app/Version.hpp>

#include <string>

#include <gtest/gtest.h>

TEST(Version, ComponentsMatchVersionString) {
    const auto composed = std::to_string(app::version::major) + "." +
        std::to_string(app::version::minor) + "." + std::to_string(app::version::patch);
    EXPECT_EQ(composed, app::version::string);
    EXPECT_FALSE(app::version::projectName.empty());
}
