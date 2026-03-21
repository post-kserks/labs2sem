#ifndef STUDENT_HPP
#define STUDENT_HPP

#include "Person.hpp"

class Student : public Person {
private:
    // 2. Ассоциация (Ученик знает своего классного руководителя, но они существуют независимо)
    Teacher* advisor; 
public:
    Student(const std::string& name, Teacher* advisor = nullptr) 
        : Person(name), advisor(advisor) {}

    void setAdvisor(Teacher* teacher) {
        advisor = teacher;
    }

    void study() const {
        std::cout << "Ученик " << name << " учится." << std::endl;
        if (advisor) {
            std::cout << "Его классный руководитель: " << advisor->getName() << std::endl;
        }
    }
};

#endif
