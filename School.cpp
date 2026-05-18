#include "School.hpp"
#include <iostream>
#include <memory>
#include <utility>

School::School(std::string name, int numClassrooms) : name(std::move(name)) {
    std::cout << "Построена школа: " << this->name << "\n";

    // Инициализация композиции: создаем аудитории, принадлежащие только школе.
    for (int i = 1; i <= numClassrooms; ++i) {
        classrooms.push_back(std::make_unique<Classroom>(i));
    }
}

School::~School() {
    std::cout << "Школа " << name << " закрывается и сносится.\n";
    // Аудитории (композиция) уничтожатся автоматически через unique_ptr.
    // Учителя (агрегация) не удаляются, т.к. школа ими не владеет.
}

void School::addTeacher(Teacher& teacher) {
    teachers.push_back(&teacher);
}

// 5. Делегирование
void School::conductLessons() const {
    std::cout << "\n--- Начинаются уроки в школе " << name << " ---\n";

    for (const std::unique_ptr<Classroom>& room : classrooms) {
        room->open();
    }

    // Школа делегирует задачу "вести уроки" объектам Teacher
    for (const Teacher* teacher : teachers) {
        teacher->teach();
    }

    std::cout << "--- Уроки завершены ---\n\n";
}
