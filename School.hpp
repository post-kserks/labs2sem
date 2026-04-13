#pragma once
#include "IPerson.hpp"
#include <vector>
#include <memory>
#include <string>

// School — хранит коллекцию людей через умные указатели на интерфейс.
// Использует композицию: школа владеет своими людьми.
// unique_ptr обеспечивает автоматическое освобождение памяти.
class School {
private:
    std::string name;
    // Контейнер умных указателей на базовый интерфейс.
    // Можно хранить любых наследников IPerson (Person, Student, GraduateStudent).
    std::vector<std::unique_ptr<IPerson>> members;

public:
    School(const std::string& name) : name(name) {}

    // Добавить члена школы. unique_ptr передаётся по перемещению (move),
    // чтобы не копировать владение.
    void addMember(std::unique_ptr<IPerson> person) {
        members.push_back(std::move(person));
    }

    // Показать всех членов школы.
    // Метод не знает конкретных типов — работает через интерфейс (полиморфизм).
    void showAll() const;

    const std::string& getName() const { return name; }
    const std::vector<std::unique_ptr<IPerson>>& getMembers() const { return members; }
};
