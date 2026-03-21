#ifndef PERSON_HPP
#define PERSON_HPP

#include <string>
#include <iostream>

// 1. Иерархия наследования (Базовый класс)
class Person {
protected:
    std::string name;
public:
    Person(const std::string& name) : name(name) {}
    virtual ~Person() = default;
    
    std::string getName() const { return name; }
    
    virtual void info() const {
        std::cout << "Человек: " << name << std::endl;
    }
};

// 1. Иерархия наследования (Производный класс 1 уровня)
class Employee : public Person {
protected:
    int salary;
public:
    Employee(const std::string& name, int salary) : Person(name), salary(salary) {}
    
    void info() const override {
        std::cout << "Сотрудник: " << name << ", Зарплата: " << salary << std::endl;
    }
};

// 1. Иерархия наследования (Производный класс 2 уровня)
class Teacher : public Employee {
private:
    std::string subject;
public:
    Teacher(const std::string& name, int salary, const std::string& subject) 
        : Employee(name, salary), subject(subject) {}
    
    // Метод, который будет вызываться при делегировании
    void teach() const {
        std::cout << "Учитель " << name << " ведет урок по предмету: " << subject << std::endl;
    }

    void info() const override {
        std::cout << "Учитель: " << name << ", Предмет: " << subject << std::endl;
    }
};

#endif
