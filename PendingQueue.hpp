#ifndef PENDINGQUEUE_HPP
#define PENDINGQUEUE_HPP

#include <cstdio>
#include <memory>
#include <queue>
#include <tuple>
#include <utility>

#include "IPending.hpp"

// Конкретный отложенный вызов: хранит функцию/метод и её аргументы.
template <typename Callable, typename... Args>
class Pending : public IPending {
private:
    Callable _callable;
    std::tuple<Args...> _args;

public:
    Pending(Callable callable, Args... args)
        : _callable(callable), _args(std::make_tuple(args...)) {}

    // Распаковываем tuple и вызываем сохранённую функцию.
    void run() override {
        std::apply(_callable, _args);
    }
};

// Очередь отложенных вызовов.
// Работает с IPending* — принцип инверсии зависимостей (DIP).
class PendingQueue : private std::queue<std::unique_ptr<IPending>> {
public:
    ~PendingQueue() {
        if (!empty()) {
            std::printf("%zu отложенных вызовов не выполнено\n", size());
        }
    }

    // Добавляет вызов в конец очереди (вариадический шаблон).
    template <typename Callable, typename... ArgTypes>
    void enqueue(Callable callable, ArgTypes... args) {
        using PendingType = Pending<Callable, ArgTypes...>;
        emplace(std::make_unique<PendingType>(callable, args...));
    }

    // Выполняет один отложенный вызов из начала очереди.
    void run_one() {
        if (empty()) {
            return;
        }
        front()->run();
        pop();
    }

    // Выполняет все отложенные вызовы по порядку.
    void run_all() {
        while (!empty()) {
            run_one();
        }
    }

    bool isEmpty() const { return empty(); }
    std::size_t count() const { return size(); }
};

#endif
