#include <iostream>

#include "Demo.hpp"
#include "MyContainer.hpp"

int main() {
    std::cout << "=== Лабораторная 7: Отсортированный связный список ===\n";
    std::cout << "Контейнер MyContainer на базе двусвязного отсортированного списка\n";
    std::cout << "Предметная область: школа, учителя\n";

    // Коллекция учителей — элементы автоматически упорядочены по зарплате.
    MyContainer<Teacher> staff;
    fillTeachers(staff);

    std::cout << "\n--- Исходный список учителей (уже отсортирован по зарплате) ---\n";
    for (auto it = staff.begin(); it != staff.end(); ++it) {
        it->printInfo();
    }

    // Прикладные задачи: поиск через алгоритмы STL.
    findTeacherByName(staff, "Петр Петрович");
    findTeacherByName(staff, "Неизвестный Учитель");

    // std::sort вызывается, но перехватывается концептом IsSortedIt (C++20).
    sortTeachersBySalary(staff);
    printTeachersWithHighSalary(staff, 50000);

    std::cout << "\nПрограмма успешно завершена.\n";
    return 0;
}
