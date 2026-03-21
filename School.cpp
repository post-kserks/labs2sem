#include "School.hpp"
#include <iostream>

School::School(const std::string& name, int numClassrooms) : name(name) {
    std::cout << "Построена школа: " << name << "\n";
    
    // Инициализация композиции (создаем части, которые принадлежат только школе)
    for (int i = 1; i <= numClassrooms; ++i) {
        classrooms.push_back(new Classroom(i));
    }
}

School::~School() {
    std::cout << "Школа " << name << " закрывается и сносится.\n";
    
    // Уничтожение композиции (части умирают вместе с целым)
    for (Classroom* room : classrooms) {
        delete room; 
    }
    // Учителя (агрегация) НЕ удаляются (delete на них не вызывается), так как они существуют сами по себе
}

void School::addTeacher(Teacher* teacher) {
    teachers.push_back(teacher);
}

// 5. Делегирование
void School::conductLessons() const {
    std::cout << "\n--- Начинаются уроки в школе " << name << " ---\n";
    
    for (const Classroom* room : classrooms) {
        room->open();
    }

    // Школа делегирует задачу "вести уроки" объектам Teacher
    for (Teacher* teacher : teachers) {
        teacher->teach();
    }
    
    std::cout << "--- Уроки завершены ---\n\n";
}
