#include <iostream>
#include <iterator>
#include <string>
extern "C" const char* Call(const char* query);
extern "C" const char* csugar_last_error();
int main() {
    std::string query((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
    const char* result = Call(query.c_str());
    const char* error = csugar_last_error();
    if (error && *error) { std::cerr << error << '\n'; return 2; }
    std::cout << result;
    return 0;
}
