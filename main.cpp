#include <iostream>
#include <memory>
#include <typeinfo>
#include <vector>

#include "Person.hpp"
#include "School.hpp"
#include "Student.hpp"
#include "Teacher.hpp"

// 3. Полиморфная функция: работает с интерфейсом, не зная конкретного типа.
void describePerson(const Person& person) {
    person.printInfo();
    std::cout << "Ключевая роль: " << person.primaryResponsibility() << "\n";
}

// 4. Демонстрация RTTI: selective access к поведению, которого нет в интерфейсе Person.
void inspectRuntimeType(const Person& person) {
    std::cout << "RTTI(typeid): " << typeid(person).name() << "\n";

    if (const auto* teacher = dynamic_cast<const Teacher*>(&person)) {
        std::cout << "dynamic_cast -> Teacher, вызов teach(): ";
        teacher->teach();
        return;
    }

    if (const auto* student = dynamic_cast<const Student*>(&person)) {
        std::cout << "dynamic_cast -> Student, вызов study(): ";
        student->study();
        return;
    }

    std::cout << "Специфичное поведение отсутствует.\n";
}

int main() {
    std::cout << "=== Семинар 4: Полиморфизм (предметная область 'Школа') ===\n\n";

    // 4. Полиморфное хранение: единый контейнер для разных типов участников.
    std::vector<std::unique_ptr<Person>> participants;
    participants.reserve(4);

    auto mathTeacher = std::make_unique<Teacher>("Иван Иванович", 50000, "Математика");
    auto physicsTeacher = std::make_unique<Teacher>("Петр Петрович", 55000, "Физика");

    Teacher* mathTeacherRef = mathTeacher.get();
    Teacher* physicsTeacherRef = physicsTeacher.get();

    participants.push_back(std::move(mathTeacher));
    participants.push_back(std::move(physicsTeacher));

    auto student = std::make_unique<Student>("Алексей");
    student->setAdvisor(mathTeacherRef);
    participants.push_back(std::move(student));

    participants.push_back(std::make_unique<Student>("Мария", physicsTeacherRef));

    std::cout << "[Полиморфная функция через интерфейс Person]\n";
    for (const std::unique_ptr<Person>& participant : participants) {
        describePerson(*participant);
        std::cout << '\n';
    }

    std::cout << "[RTTI: typeid + dynamic_cast]\n";
    for (const std::unique_ptr<Person>& participant : participants) {
        inspectRuntimeType(*participant);
        std::cout << '\n';
    }

    {
        // 3. Композиция (Classroom) + 4. Агрегация (Teacher*) + 5. Делегирование.
        School mySchool("Школа Лицей №1", 2);
        mySchool.addTeacher(*mathTeacherRef);
        mySchool.addTeacher(*physicsTeacherRef);

        std::cout << "[Агрегация, Композиция и Делегирование]\n";
        mySchool.conductLessons();

        std::cout << "[Завершение области видимости школы...]\n";
    } // mySchool уничтожается, а учителя продолжают жить в participants.

    std::cout << "\nДоказательство агрегации: школа уничтожена, но учителя доступны:\n";
    mathTeacherRef->printInfo();

    std::cout << "\nПрограмма успешно завершена.\n";
    return 0;
}
