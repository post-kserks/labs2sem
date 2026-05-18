#include <iostream>

#include "Demo.hpp"
#include "MyContainer.hpp"

int main() {
    std::cout << "=== Семинар 5: Коллекция MyContainer и итераторы ===\n";
    std::cout << "Предметная область: школа, учителя\n";

    // Коллекция учителей — один объект хранит всех сотрудников.
    MyContainer<Teacher> staff;
    fillTeachers(staff);

    std::cout << "\n--- Исходный список учителей ---\n";
    for (auto it = staff.begin(); it != staff.end(); ++it) {
        it->printInfo();
    }

    // Прикладные задачи: поиск и сортировка через алгоритмы STL.
    findTeacherByName(staff, "Петр Петрович");
    findTeacherByName(staff, "Неизвестный Учитель");

    sortTeachersBySalary(staff);
    printTeachersWithHighSalary(staff, 50000);

    std::cout << "\nПрограмма успешно завершена.\n";
    return 0;
}
