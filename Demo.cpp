#include "Demo.hpp"

#include <cstdio>
#include <functional>
#include <iostream>

#include "MyContainer.hpp"
#include "PendingQueue.hpp"
#include "School.hpp"
#include "Student.hpp"
#include "Teacher.hpp"

// Свободная функция — пример отложенного вызова не-метода.
static void printMessage(const char* text) {
    std::cout << "[отложенный вызов] " << text << '\n';
}

// Обёртки с выводом: сами методы addTeacher и push_back молчат,
// поэтому без них кажется, что шаг «не сработал».
static void addTeacherLogged(School* school, Teacher& teacher) {
    school->addTeacher(teacher);
    std::cout << "School::addTeacher — добавлен " << teacher.getName() << '\n';
}

static void pushBackLogged(MyContainer<Teacher>* staff, Teacher teacher) {
    staff->push_back(teacher);
    std::cout << "MyContainer::push_back — добавлен " << teacher.getName() << '\n';
}

void runPendingQueueDemo() {
    std::cout << "=== Семинар 6: Очередь отложенных вызовов ===\n";
    std::cout << "Предметная область: школа\n\n";

    PendingQueue queue;

    // Объекты предметной области — должны жить до выполнения очереди.
    School school("Гимназия №1", 2);
    Teacher ivan("Иван Иванович", 50000, "Математика");
    Teacher maria("Мария Сергеевна", 55000, "Физика");
    Student vasya("Сидор Сидоров", &ivan);
    MyContainer<Teacher> staff;

    std::cout << "--- Добавляем вызовы в очередь (enqueue) ---\n";

    // 1. Отложенный вызов стандартной функции printf.
    queue.enqueue(printf, "Hello, %s\n", "world");

    // 2. Отложенный вызов свободной функции предметной области.
    queue.enqueue(printMessage, "Школа готовится к новому учебному дню");

    // 3–4. Отложенный вызов метода School::addTeacher (через обёртку с логом).
    // std::ref нужен, чтобы в tuple сохранилась ссылка, а не копия объекта.
    queue.enqueue(addTeacherLogged, &school, std::ref(ivan));
    queue.enqueue(addTeacherLogged, &school, std::ref(maria));

    // 5. Отложенный вызов MyContainer::push_back (через обёртку с логом).
    queue.enqueue(pushBackLogged, &staff, Teacher("Петр Петрович", 60000, "Химия"));

    // 5. Отложенный вызов метода Student::study.
    queue.enqueue(&Student::study, &vasya);

    // 6. Отложенный вызов метода School::conductLessons (делегирование).
    queue.enqueue(&School::conductLessons, &school);

    std::cout << "В очереди " << queue.count() << " вызов(ов)\n\n";

    // Выполняем по одному — метод run_one из задания.
    std::cout << "--- Выполняем вызовы по одному (run_one) ---\n";
    int step = 1;
    while (!queue.isEmpty()) {
        std::cout << "Шаг " << step++ << ":\n";
        queue.run_one();
        std::cout << '\n';
    }

    std::cout << "--- Учителя в коллекции MyContainer ---\n";
    for (auto it = staff.begin(); it != staff.end(); ++it) {
        it->printInfo();
    }

    std::cout << "\n--- Пример run_all: все вызовы сразу ---\n";
    PendingQueue batch;
    batch.enqueue(printMessage, "Первый пакетный вызов");
    batch.enqueue(printMessage, "Второй пакетный вызов");
    batch.run_all();
}
