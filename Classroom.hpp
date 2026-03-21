#ifndef CLASSROOM_HPP
#define CLASSROOM_HPP

#include <iostream>

class Classroom {
private:
    int number;
public:
    Classroom(int num) : number(num) {
        std::cout << "  [Композиция] Создана аудитория номер " << number << "\n";
    }
    
    ~Classroom() {
        std::cout << "  [Композиция] Разрушена аудитория номер " << number << "\n";
    }

    void open() const {
        std::cout << "Аудитория " << number << " открыта для занятий.\n";
    }
};

#endif
