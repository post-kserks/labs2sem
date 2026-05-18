#ifndef MYCONTAINER_HPP
#define MYCONTAINER_HPP

#include <cstddef>
#include <iterator>
#include <stdexcept>

// Шаблонная коллекция — динамический массив для хранения объектов любого типа T.
template <typename T>
class MyContainer {
private:
    T* data;
    size_t size_;
    size_t capacity_;

    // Увеличивает ёмкость массива при нехватке места.
    void resize(size_t new_capacity) {
        // Выделяем память без вызова конструкторов (Teacher не имеет конструктора по умолчанию).
        T* new_data = static_cast<T*>(::operator new(new_capacity * sizeof(T)));
        for (size_t i = 0; i < size_; ++i) {
            new (new_data + i) T(std::move(data[i]));
            data[i].~T();
        }
        ::operator delete(data);
        data = new_data;
        capacity_ = new_capacity;
    }

    // Явно вызываем деструкторы всех элементов.
    void destroyElements() {
        for (size_t i = 0; i < size_; ++i) {
            data[i].~T();
        }
    }

public:
    MyContainer() : data(nullptr), size_(0), capacity_(0) {}

    ~MyContainer() {
        destroyElements();
        ::operator delete(data);
    }

    // Запрещаем копирование — достаточно для лабораторной, избегаем лишнего кода.
    MyContainer(const MyContainer&) = delete;
    MyContainer& operator=(const MyContainer&) = delete;

    // Добавляет элемент в конец коллекции.
    void push_back(const T& value) {
        if (size_ >= capacity_) {
            size_t new_cap = (capacity_ == 0) ? 1 : capacity_ * 2;
            resize(new_cap);
        }
        new (data + size_) T(value);
        ++size_;
    }

    // Удаляет последний элемент (если коллекция не пуста).
    void pop_back() {
        if (size_ > 0) {
            --size_;
            data[size_].~T();
        }
    }

    // Доступ к элементу по индексу.
    T& operator[](size_t index) {
        if (index >= size_) {
            throw std::out_of_range("MyContainer: индекс вне диапазона");
        }
        return data[index];
    }

    const T& operator[](size_t index) const {
        if (index >= size_) {
            throw std::out_of_range("MyContainer: индекс вне диапазона");
        }
        return data[index];
    }

    size_t getSize() const { return size_; }
    bool empty() const { return size_ == 0; }

    // Внутренний итератор коллекции.
    class Iterator {
    private:
        T* ptr;

    public:
        // Характеристики итератора для std::iterator_traits и алгоритмов STL.
        using iterator_category = std::random_access_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = T*;
        using reference = T&;

        explicit Iterator(T* p = nullptr) : ptr(p) {}

        reference operator*() { return *ptr; }
        pointer operator->() { return ptr; }
        reference operator*() const { return *ptr; }
        pointer operator->() const { return ptr; }

        // Переход к следующему элементу (префиксный ++).
        Iterator& operator++() {
            ++ptr;
            return *this;
        }

        Iterator operator++(int) {
            Iterator old = *this;
            ++ptr;
            return old;
        }

        // Переход к предыдущему элементу (для random_access).
        Iterator& operator--() {
            --ptr;
            return *this;
        }

        Iterator operator--(int) {
            Iterator old = *this;
            --ptr;
            return old;
        }

        Iterator& operator+=(difference_type n) {
            ptr += n;
            return *this;
        }

        Iterator& operator-=(difference_type n) {
            ptr -= n;
            return *this;
        }

        Iterator operator+(difference_type n) const { return Iterator(ptr + n); }
        Iterator operator-(difference_type n) const { return Iterator(ptr - n); }

        reference operator[](difference_type n) { return ptr[n]; }

        difference_type operator-(const Iterator& other) const {
            return ptr - other.ptr;
        }

        bool operator==(const Iterator& other) const { return ptr == other.ptr; }
        bool operator!=(const Iterator& other) const { return ptr != other.ptr; }
        bool operator<(const Iterator& other) const { return ptr < other.ptr; }
        bool operator>(const Iterator& other) const { return ptr > other.ptr; }
        bool operator<=(const Iterator& other) const { return ptr <= other.ptr; }
        bool operator>=(const Iterator& other) const { return ptr >= other.ptr; }
    };

    Iterator begin() { return Iterator(data); }
    Iterator end() { return Iterator(data + size_); }

    Iterator begin() const { return Iterator(data); }
    Iterator end() const { return Iterator(data + size_); }
};

#endif
