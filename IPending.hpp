#ifndef IPENDING_HPP
#define IPENDING_HPP

// Базовый интерфейс отложенного вызова.
// Один метод run() — принцип единственной ответственности (SRP).
class IPending {
public:
    virtual ~IPending() = default;

    // Выполняет сохранённый вызов.
    virtual void run() = 0;
};

#endif
