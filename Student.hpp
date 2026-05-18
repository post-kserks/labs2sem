#ifndef STUDENT_HPP
#define STUDENT_HPP

#include <iostream>
#include <string>
#include <utility>

#include "Person.hpp"
#include "Teacher.hpp"

class Student : public Person {
private:
    // 2. Ассоциация: невладеющая ссылка на классного руководителя.
    Teacher* advisor;

public:
    explicit Student(std::string name, Teacher* advisor = nullptr)
        : Person(std::move(name)), advisor(advisor) {}

    void setAdvisor(Teacher* teacher) {
        advisor = teacher;
    }

    void printInfo() const override {
        std::cout << "Ученик: " << name;
        if (advisor) {
            std::cout << " (классный руководитель: " << advisor->getName() << ")";
        }
        std::cout << '\n';
    }

    std::string primaryResponsibility() const override {
        return "Осваивает учебную программу";
    }

    void study() const {
        std::cout << "Ученик " << name << " учится.\n";
        if (advisor) {
            std::cout << "Его классный руководитель: " << advisor->getName() << '\n';
        }
    }
};

#endif
