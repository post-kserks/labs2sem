#ifndef PERSON_HPP
#define PERSON_HPP

#include <string>
#include <utility>

// Базовый интерфейс для всех участников школьной системы.
class Person {
protected:
    std::string name;

public:
    explicit Person(std::string name) : name(std::move(name)) {}
    virtual ~Person() = default;

    const std::string& getName() const noexcept { return name; }

    // Ключевое полиморфное поведение.
    virtual void printInfo() const = 0;
    virtual std::string primaryResponsibility() const = 0;
};

#endif
