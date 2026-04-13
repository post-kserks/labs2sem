#include "School.hpp"
#include "Person.hpp"
#include "Student.hpp"
#include "GraduateStudent.hpp"
#include <iostream>
#include <memory>
#include <typeinfo>

// Полиморфная функция — принимает ССЫЛКУ на интерфейс IPerson.
// Не знает ничего о конкретном типе объекта.
// За счёт виртуальных методов вызывается правильная реализация.
void describeParticipant(const IPerson& person) {
    std::cout << ">> Участник: ";
    person.printInfo(); // вызывается нужная реализация — полиморфизм!
    std::cout << "   Роль: " << person.getRole() << "\n\n";
}

int main() {
    // --- 1. Создаём школу и заполняем контейнер умными указателями ---
    School school("МГТУ им. Баумана");

    // make_unique создаёт объект и возвращает unique_ptr.
    // Все три типа хранятся в одном контейнере через указатель на IPerson.
    school.addMember(std::make_unique<Person>("Иванов И.И."));
    school.addMember(std::make_unique<Student>("Петров П.П.", 10));
    school.addMember(std::make_unique<Student>("Сидорова А.А.", 11));
    school.addMember(std::make_unique<GraduateStudent>("Козлов В.В.", 12, "Алгоритмы сортировки"));

    // --- 2. Полиморфный обход контейнера (вызов через School::showAll) ---
    school.showAll();
    std::cout << "\n";

    // --- 3. Полиморфная функция — демонстрируем вызов с разными типами ---
    std::cout << "--- Полиморфная функция describeParticipant ---\n";
    Person    p("Новиков Н.Н.");
    Student   s("Морозов М.М.", 9);
    GraduateStudent g("Волкова В.В.", 12, "Теория чисел");

    describeParticipant(p);
    describeParticipant(s);
    describeParticipant(g);

    // --- 4. dynamic_cast и typeid ---
    // dynamic_cast нужен, когда нужно добраться до метода, которого нет в интерфейсе.
    // Пример: getThesisTheme() есть только у GraduateStudent, не у IPerson.
    // ВАЖНО: злоупотреблять dynamic_cast — признак плохой архитектуры (нарушение LSP).
    // Используем только в демонстрационных целях.
    std::cout << "--- Демонстрация dynamic_cast и typeid ---\n";
    const auto& members = school.getMembers();
    for (const auto& member : members) {
        // typeid возвращает информацию о фактическом типе объекта во время выполнения.
        // Берём сырой указатель отдельно, чтобы typeid не видел «побочных эффектов».
        const IPerson* raw = member.get();
        std::cout << "typeid: " << typeid(*raw).name() << "\n";

        // dynamic_cast вернёт nullptr, если тип не совпадает
        const GraduateStudent* grad = dynamic_cast<const GraduateStudent*>(member.get());
        if (grad) {
            std::cout << "  -> Это аспирант! Тема диссертации: \""
                      << grad->getThesisTheme() << "\"\n";
        }
    }

    // unique_ptr автоматически освобождает память при выходе из main.
    // Виртуальный деструктор в IPerson гарантирует вызов нужного деструктора.
    return 0;
}
