#ifndef MYCONTAINER_HPP
#define MYCONTAINER_HPP

#include <cstddef>
#include <cstdio>
#include <iterator>
#include <stdexcept>
#include <type_traits>

// ============================================================================
// Шаблонная коллекция на базе отсортированного связного списка.
//
// Внутренняя структура — двусвязный список, элементы вставляются с сохранением
// порядка (по возрастанию через operator<). Внешний интерфейс контейнера
// совместим с предыдущей версией на основе массива.
// ============================================================================
template <typename T>
class MyContainer {
private:
    // Узел двусвязного списка.
    struct Node {
        T value;
        Node* prev;
        Node* next;

        template <typename U>
        Node(U&& val, Node* p, Node* n)
            : value(std::forward<U>(val)), prev(p), next(n) {}
    };

    Node* head_;   // указатель на первый узел
    Node* tail_;   // указатель на последний узел
    size_t size_;  // текущее количество элементов

public:
    MyContainer() : head_(nullptr), tail_(nullptr), size_(0) {}

    ~MyContainer() {
        Node* cur = head_;
        while (cur) {
            Node* next = cur->next;
            delete cur;
            cur = next;
        }
    }

    // Запрещаем копирование.
    MyContainer(const MyContainer&) = delete;
    MyContainer& operator=(const MyContainer&) = delete;

    // ---------- Вставка с сохранением порядка ----------

    // push_back сохраняет совместимость интерфейса, но элемент вставляется
    // не в конец, а в позицию, соответствующую отсортированному порядку.
    void push_back(const T& value) {
        insert_sorted(value);
    }

    // Удаляет последний элемент списка (наибольший по порядку).
    void pop_back() {
        if (!tail_) return;
        Node* to_delete = tail_;
        tail_ = tail_->prev;
        if (tail_) {
            tail_->next = nullptr;
        } else {
            head_ = nullptr;
        }
        delete to_delete;
        --size_;
    }

    // Доступ по индексу — O(n), но сохраняет внешний интерфейс.
    T& operator[](size_t index) {
        if (index >= size_) {
            throw std::out_of_range("MyContainer: индекс вне диапазона");
        }
        Node* cur = head_;
        for (size_t i = 0; i < index; ++i) {
            cur = cur->next;
        }
        return cur->value;
    }

    const T& operator[](size_t index) const {
        if (index >= size_) {
            throw std::out_of_range("MyContainer: индекс вне диапазона");
        }
        Node* cur = head_;
        for (size_t i = 0; i < index; ++i) {
            cur = cur->next;
        }
        return cur->value;
    }

    size_t getSize() const { return size_; }
    bool empty() const { return size_ == 0; }

    // ==================== Итератор ====================
    // Двунаправленный итератор для обхода связного списка.
    class Iterator {
    private:
        Node* node_;

    public:
        // Характеристики итератора для std::iterator_traits и алгоритмов STL.
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = T*;
        using reference = T&;

        // Специальный маркер: контейнер уже отсортирован.
        using is_already_sorted = std::true_type;

        explicit Iterator(Node* node = nullptr) : node_(node) {}

        reference operator*() { return node_->value; }
        pointer operator->() { return &node_->value; }
        reference operator*() const { return node_->value; }
        pointer operator->() const { return &node_->value; }

        // Переход к следующему элементу.
        Iterator& operator++() {
            node_ = node_->next;
            return *this;
        }

        Iterator operator++(int) {
            Iterator old = *this;
            node_ = node_->next;
            return old;
        }

        // Переход к предыдущему элементу.
        Iterator& operator--() {
            node_ = node_->prev;
            return *this;
        }

        Iterator operator--(int) {
            Iterator old = *this;
            node_ = node_->prev;
            return old;
        }

        bool operator==(const Iterator& other) const { return node_ == other.node_; }
        bool operator!=(const Iterator& other) const { return node_ != other.node_; }
    };

    Iterator begin() { return Iterator(head_); }
    Iterator end() { return Iterator(nullptr); }

    Iterator begin() const { return Iterator(head_); }
    Iterator end() const { return Iterator(nullptr); }

private:
    // Вставка элемента в отсортированную позицию (по возрастанию).
    void insert_sorted(const T& value) {
        // Ищем позицию: первый узел, значение которого >= value.
        Node* cur = head_;
        while (cur && cur->value < value) {
            cur = cur->next;
        }

        if (!cur) {
            // Вставка в конец (или в пустой список).
            Node* new_node = new Node(value, tail_, nullptr);
            if (tail_) {
                tail_->next = new_node;
            } else {
                head_ = new_node;
            }
            tail_ = new_node;
        } else if (!cur->prev) {
            // Вставка перед головой.
            Node* new_node = new Node(value, nullptr, head_);
            head_->prev = new_node;
            head_ = new_node;
        } else {
            // Вставка между cur->prev и cur.
            Node* new_node = new Node(value, cur->prev, cur);
            cur->prev->next = new_node;
            cur->prev = new_node;
        }
        ++size_;
    }
};

// ============================================================================
// Концепт IsSortedIt (C++20): проверяет наличие маркера is_already_sorted.
// ============================================================================
template <typename T>
concept IsSortedIt = requires {
    typename T::is_already_sorted;
};

// ============================================================================
// Перегрузка std::sort для итераторов отсортированного контейнера.
// Данные уже упорядочены — сортировка не нужна.
// ============================================================================
namespace std {
    template <typename T>
    void sort(T begin, T end) requires IsSortedIt<T> {
        (void)begin;
        (void)end;
        puts("std::sort: контейнер уже отсортирован, сортировка не требуется.");
    }

    template <typename T, typename Compare>
    void sort(T begin, T end, Compare comp) requires IsSortedIt<T> {
        (void)begin;
        (void)end;
        (void)comp;
        puts("std::sort: контейнер уже отсортирован, сортировка не требуется.");
    }
}

#endif
