#include <iostream>
#include "Person.hpp"
#include "Student.hpp"
#include "School.hpp"

int main() {
    std::cout << "=== Демонстрация ООП: Предметная область 'Школа' ===\n\n";

    // 1. Иерархия наследования: Person -> Employee -> Teacher
    Teacher mathTeacher("Иван Иванович", 50000, "Математика");
    Teacher physicsTeacher("Петр Петрович", 55000, "Физика");

    std::cout << "[Иерархия объектов:]\n";
    mathTeacher.info();
    physicsTeacher.info();
    std::cout << "\n";

    // 2. Ассоциация: Ученик и Учитель (классный руководитель)
    Student student1("Алексей");
    student1.setAdvisor(&mathTeacher);

    std::cout << "[Ассоциация:]\n";
    student1.study();
    std::cout << "\n";

    {
        // 3. Композиция: Школа при создании генерирует свои аудитории внутри себя
        School mySchool("Школа Лицей №1", 2);

        // 4. Агрегация: Передаем существующих учителей в школу.
        // Школа коллекционирует указатели, но учителя не привязаны жестко к школе.
        mySchool.addTeacher(&mathTeacher);
        mySchool.addTeacher(&physicsTeacher);

        // 5. Делегирование: Школа делегирует процесс преподавания своим учителям
        std::cout << "\n[Агрегация, Композиция и Делегирование:]\n";
        mySchool.conductLessons();
        
        std::cout << "[Завершение области видимости школы...]\n";
    } // Здесь вызывается деструктор mySchool
    
    std::cout << "\nДоказательство Агрегации: школа уничтожена, но учителя остались целы:\n";
    mathTeacher.info();

    std::cout << "\nПрограмма успешно завершена.\n";
    return 0;
}
