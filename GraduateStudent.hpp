#pragma once
#include "Student.hpp"

// GraduateStudent — аспирант/выпускник, наследник Student.
// Добавляет тему диссертации.
// final — запрещает дальнейшее наследование от этого класса.
class GraduateStudent final : public Student {
private:
    std::string thesisTheme; // тема диссертации

public:
    GraduateStudent(const std::string& name, int grade, const std::string& theme)
        : Student(name, grade), thesisTheme(theme) {}

    // final — запрещает переопределение в несуществующих подклассах (компилятор проверит)
    void printInfo() const override final {
        std::cout << "[GraduateStudent] Имя: " << name
                  << ", Класс: " << grade
                  << ", Диссертация: \"" << thesisTheme << "\"\n";
    }

    std::string getRole() const override final {
        return "Аспирант";
    }

    // Специфичный метод — НЕТ в интерфейсе IPerson.
    // Доступен только при приведении типа к GraduateStudent*.
    const std::string& getThesisTheme() const { return thesisTheme; }
};
