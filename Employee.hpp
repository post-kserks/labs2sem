#ifndef EMPLOYEE_HPP
#define EMPLOYEE_HPP

#include <iostream>
#include <string>

#include "Person.hpp"

// 1. Иерархия наследования (уровень 1): Person -> Employee
class Employee : public Person {
protected:
    int salary;

public:
    Employee(std::string name, int salary) : Person(std::move(name)), salary(salary) {}

    int getSalary() const noexcept { return salary; }

    void printInfo() const override {
        std::cout << "Сотрудник: " << name << ", зарплата: " << salary << '\n';
    }

    std::string primaryResponsibility() const override {
        return "Обеспечивает работу школы";
    }
};

#endif
