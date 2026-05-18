#include "Demo.hpp"

#include <algorithm>
#include <iostream>

void fillTeachers(MyContainer<Teacher>& staff) {
    staff.push_back(Teacher("Иван Иванович", 50000, "Математика"));
    staff.push_back(Teacher("Петр Петрович", 55000, "Физика"));
    staff.push_back(Teacher("Анна Сергеевна", 48000, "Литература"));
    staff.push_back(Teacher("Ольга Николаевна", 62000, "Информатика"));
}

void findTeacherByName(const MyContainer<Teacher>& staff, const std::string& name) {
    // Для std::find создаём «образец» — учитель с нужным именем.
    Teacher searchTemplate(name, 0, "");

    auto it = std::find(staff.begin(), staff.end(), searchTemplate);

    std::cout << "\n--- Поиск учителя (std::find) ---\n";
    if (it != staff.end()) {
        std::cout << "Найден: ";
        it->printInfo();
    } else {
        std::cout << "Учитель \"" << name << "\" не найден.\n";
    }
}

void sortTeachersBySalary(MyContainer<Teacher>& staff) {
    // std::sort работает с итераторами random_access — сортируем по зарплате.
    std::sort(staff.begin(), staff.end(),
              [](const Teacher& a, const Teacher& b) {
                  return a.getSalary() < b.getSalary();
              });

    std::cout << "\n--- Список учителей после сортировки по зарплате (std::sort) ---\n";
    for (auto it = staff.begin(); it != staff.end(); ++it) {
        it->printInfo();
    }
}

void printTeachersWithHighSalary(const MyContainer<Teacher>& staff, int minSalary) {
    std::cout << "\n--- Учителя с зарплатой выше " << minSalary << " (обход итераторами) ---\n";

    // Классический обход коллекции через begin/end.
    for (auto it = staff.begin(); it != staff.end(); ++it) {
        if (it->getSalary() > minSalary) {
            it->printInfo();
        }
    }
}
