# Семинар 4 — Полиморфизм в C++

**Предметная область:** Школа  
**Язык:** C++17  
**Сборка:** `make`

---

## Цель работы

Модифицировать структуру классов из предыдущего семинара (наследование, агрегация, композиция), добавив полиморфное поведение:

- абстрактный интерфейс с чистыми виртуальными функциями
- иерархию классов с переопределением методов (`override`, `final`)
- полиморфную функцию, работающую через указатель/ссылку на базовый класс
- контейнер умных указателей (`unique_ptr`) с полиморфным обходом
- демонстрацию `dynamic_cast` и `typeid`

---

## Структура проекта

```
.
├── IPerson.hpp          # Абстрактный интерфейс — «контракт» для всех участников
├── Person.hpp           # Базовый класс, реализует IPerson
├── Student.hpp          # Наследник Person, добавляет номер класса
├── GraduateStudent.hpp  # Наследник Student (final), добавляет тему диссертации
├── School.hpp           # Класс школы — хранит вектор unique_ptr<IPerson>
├── School.cpp           # Реализация метода School::showAll
├── main.cpp             # Точка входа, демонстрация всех возможностей
└── Makefile             # Сборка проекта
```

---

## Иерархия классов

```
IPerson           ← абстрактный интерфейс (printInfo, getRole)
  └── Person      ← конкретный класс, "Человек"
        └── Student        ← "Ученик", добавляет номер класса
              └── GraduateStudent (final) ← "Аспирант", добавляет тему диссертации
```

---

## Сборка и запуск

```bash
# Собрать проект
make

# Запустить
./school

# Пересобрать с нуля
make clean && make
```

---

## Демонстрируемые концепции

### 1. Абстрактный интерфейс (`IPerson.hpp`)

Класс `IPerson` содержит две чистые виртуальные функции и виртуальный деструктор.  
Создать объект `IPerson` напрямую невозможно — он задаёт только контракт.

```cpp
class IPerson {
public:
    virtual void printInfo() const = 0;   // чистая виртуальная
    virtual std::string getRole() const = 0;
    virtual ~IPerson() = default;         // виртуальный деструктор
};
```

### 2. Иерархия с `override` и `final`

Каждый производный класс переопределяет методы интерфейса с ключевым словом `override`.  
`GraduateStudent` помечен `final` — от него нельзя наследоваться.

```cpp
class GraduateStudent final : public Student {
    void printInfo() const override final { ... }
    std::string getRole() const override final { return "Аспирант"; }
};
```

### 3. Полиморфная функция

Функция `describeParticipant` принимает **ссылку на интерфейс** и не знает конкретного типа объекта.  
Нужная реализация выбирается автоматически во время выполнения (динамическое связывание).

```cpp
void describeParticipant(const IPerson& person) {
    person.printInfo();
    std::cout << person.getRole();
}
```

### 4. Полиморфное хранение (`School`)

В классе `School` объекты хранятся через `unique_ptr<IPerson>`.  
Это позволяет держать `Person`, `Student` и `GraduateStudent` в одном контейнере.  
`unique_ptr` автоматически освобождает память — вручную `delete` не нужен.

```cpp
std::vector<std::unique_ptr<IPerson>> members;

school.addMember(std::make_unique<Student>("Петров", 10));
school.addMember(std::make_unique<GraduateStudent>("Козлов", 12, "Алгоритмы"));
```

### 5. `dynamic_cast` и `typeid`

`typeid` позволяет узнать фактический тип объекта во время выполнения.  
`dynamic_cast` даёт доступ к методам, которых нет в интерфейсе (`getThesisTheme`).

> ⚠️ Злоупотребление `dynamic_cast` — признак нарушения **принципа подстановки Лисков (LSP)**.  
> Если код постоянно проверяет типы, значит интерфейс спроектирован неверно.  
> Здесь `dynamic_cast` используется **только в демонстрационных целях**.

```cpp
const GraduateStudent* grad = dynamic_cast<const GraduateStudent*>(member.get());
if (grad) {
    std::cout << grad->getThesisTheme();
}
```

---

## Пример вывода

```
=== Школа: МГТУ им. Баумана ===
[Person] Имя: Иванов И.И.
  Роль: Человек
[Student] Имя: Петров П.П., Класс: 10
  Роль: Ученик
[Student] Имя: Сидорова А.А., Класс: 11
  Роль: Ученик
[GraduateStudent] Имя: Козлов В.В., Класс: 12, Диссертация: "Алгоритмы сортировки"
  Роль: Аспирант

--- Полиморфная функция describeParticipant ---
>> Участник: [Person] Имя: Новиков Н.Н.
   Роль: Человек

>> Участник: [Student] Имя: Морозов М.М., Класс: 9
   Роль: Ученик

>> Участник: [GraduateStudent] Имя: Волкова В.В., Класс: 12, Диссертация: "Теория чисел"
   Роль: Аспирант

--- Демонстрация dynamic_cast и typeid ---
typeid: 6Person
typeid: 7Student
typeid: 7Student
typeid: 15GraduateStudent
  -> Это аспирант! Тема диссертации: "Алгоритмы сортировки"
```
