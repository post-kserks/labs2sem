#ifndef SCHOOL_HPP
#define SCHOOL_HPP

#include <memory>
#include <string>
#include <vector>

#include "Classroom.hpp"
#include "Teacher.hpp"

class School {
private:
    std::string name;

    // 3. Композиция: аудитории живут и умирают вместе со школой.
    std::vector<std::unique_ptr<Classroom>> classrooms;

    // 4. Агрегация: школа не владеет учителями.
    std::vector<Teacher*> teachers;

public:
    School(std::string name, int numClassrooms);
    ~School();

    void addTeacher(Teacher& teacher);

    // 5. Делегирование: Школа поручает ведение уроков учителям
    void conductLessons() const;
};

#endif
