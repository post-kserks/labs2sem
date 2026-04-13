#include "School.hpp"
#include <iostream>
#include <typeinfo>

// Реализация метода showAll.
// Перебирает всех членов школы и вызывает printInfo() через указатель на IPerson.
// Благодаря полиморфизму вызывается реализация нужного класса — Person, Student или GraduateStudent.
void School::showAll() const {
    std::cout << "=== Школа: " << name << " ===\n";
    for (const auto& member : members) {
        // Вызов виртуального метода — динамическое связывание в действии.
        // Какой именно printInfo() будет вызван — решается во время выполнения.
        member->printInfo();
        std::cout << "  Роль: " << member->getRole() << "\n";
    }
}
