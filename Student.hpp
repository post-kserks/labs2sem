#pragma once
#include "Person.hpp"

// Класс Student наследуется от Person.
// Добавляет номер класса (grade) и переопределяет методы интерфейса.
class Student : public Person {
protected:
    int grade; // номер класса (1-11)

public:
    Student(const std::string& name, int grade)
        : Person(name), grade(grade) {}

    // override — переопределяем метод из интерфейса.
    // Компилятор проверит, что такой метод есть в базовом классе.
    void printInfo() const override {
        std::cout << "[Student] Имя: " << name
                  << ", Класс: " << grade << "\n";
    }

    std::string getRole() const override {
        return "Ученик";
    }

    int getGrade() const { return grade; }
};
