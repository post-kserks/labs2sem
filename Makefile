CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17

TARGET = school_app
SRCS = main.cpp Demo.cpp School.cpp
OBJS = $(SRCS:.cpp=.o)

# Заголовочные файлы проекта (шаблоны и классы предметной области)
HEADERS = MyContainer.hpp Demo.hpp \
          Person.hpp Employee.hpp Teacher.hpp Student.hpp \
          Classroom.hpp School.hpp

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Команда для просмотра структуры проекта лабораторной
structure:
	@echo "Структура проекта (лабораторная 5):"
	@echo ""
	@echo "  MyContainer.hpp  — шаблонная коллекция с итератором"
	@echo "  Demo.hpp/cpp     — прикладные функции (find, sort, обход)"
	@echo "  main.cpp         — точка входа"
	@echo "  Person.hpp       — базовый класс"
	@echo "  Employee.hpp     — сотрудник"
	@echo "  Teacher.hpp      — учитель"
	@echo "  Student.hpp      — ученик"
	@echo "  Classroom.hpp    — аудитория"
	@echo "  School.hpp/cpp   — школа (из прошлых семинаров)"
	@echo "  Makefile         — сборка: make / make run / make clean"
	@echo ""

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run structure
