#ifndef DEMO_HPP
#define DEMO_HPP

#include "MyContainer.hpp"
#include "Teacher.hpp"

// Заполняет коллекцию учителями школы.
void fillTeachers(MyContainer<Teacher>& staff);

// Прикладная задача: найти учителя по имени через std::find.
void findTeacherByName(const MyContainer<Teacher>& staff, const std::string& name);

// Прикладная задача: отсортировать учителей по зарплате через std::sort.
void sortTeachersBySalary(MyContainer<Teacher>& staff);

// Выводит учителей с зарплатой выше порога, обходя коллекцию итераторами.
void printTeachersWithHighSalary(const MyContainer<Teacher>& staff, int minSalary);

#endif
