#ifndef SCHOOL_HPP
#define SCHOOL_HPP

#include <vector>
#include <string>
#include "Person.hpp"
#include "Classroom.hpp"

class School {
private:
    std::string name;
    
    // 3. Композиция: Аудитории жестко привязаны к школе (уничтожаются вместе с ней)
    std::vector<Classroom*> classrooms;
    
    // 4. Агрегация: Школа хранит указатели на учителей, но они продолжат существовать и без школы
    std::vector<Teacher*> teachers;

public:
    School(const std::string& name, int numClassrooms);
    ~School();

    void addTeacher(Teacher* teacher);
    
    // 5. Делегирование: Школа поручает ведение уроков учителям
    void conductLessons() const;
};

#endif
