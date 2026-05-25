#ifndef TEACHER_HPP
#define TEACHER_HPP

#include <iostream>
#include <string>

#include "Employee.hpp"

// 1. Иерархия наследования (уровень 2): Person -> Employee -> Teacher
class Teacher : public Employee {
private:
    std::string subject;

public:
    Teacher(std::string name, int salary, std::string subject)
        : Employee(std::move(name), salary), subject(std::move(subject)) {}

    const std::string& getSubject() const noexcept { return subject; }

    // Используется в делегировании.
    void teach() const {
        std::cout << "Учитель " << name << " ведет урок по предмету: " << subject << '\n';
    }

    void printInfo() const override {
        std::cout << "Учитель: " << name << ", предмет: " << subject
                  << ", зарплата: " << salary << '\n';
    }

    std::string primaryResponsibility() const override {
        return "Проводит занятия по предмету " + subject;
    }

    // Нужен для std::find — сравниваем учителей по имени.
    bool operator==(const Teacher& other) const {
        return getName() == other.getName();
    }

    // Нужен для отсортированного контейнера — сортируем по зарплате.
    bool operator<(const Teacher& other) const {
        return salary < other.salary;
    }
};

#endif
