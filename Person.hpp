#pragma once
#include "IPerson.hpp"
#include <iostream>

// Базовый конкретный класс — реализует интерфейс IPerson.
// Представляет любого человека в школе (не обязательно ученика).
class Person : public IPerson {
protected:
    std::string name; // имя человека

public:
    // Конструктор принимает имя
    Person(const std::string& name) : name(name) {}

    // Реализуем чистую виртуальную функцию из интерфейса
    void printInfo() const override {
        std::cout << "[Person] Имя: " << name << "\n";
    }

    // Реализуем getRole — Person это просто "Человек"
    std::string getRole() const override {
        return "Человек";
    }

    // Геттер имени — пригодится в производных классах
    const std::string& getName() const { return name; }
};
