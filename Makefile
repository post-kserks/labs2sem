CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17

TARGET = school_app
SRCS = main.cpp Demo.cpp School.cpp
OBJS = $(SRCS:.cpp=.o)

HEADERS = IPending.hpp PendingQueue.hpp Demo.hpp \
          MyContainer.hpp \
          Person.hpp Employee.hpp Teacher.hpp Student.hpp \
          Classroom.hpp School.hpp

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Показать структуру проекта лабораторной
structure:
	@echo "Структура проекта (семинар 6):"
	@echo ""
	@echo "  IPending.hpp     — интерфейс отложенного вызова"
	@echo "  PendingQueue.hpp — шаблон Pending и очередь PendingQueue"
	@echo "  Demo.hpp/cpp     — демонстрация enqueue / run_one / run_all"
	@echo "  main.cpp         — точка входа"
	@echo "  Person.hpp       — базовый класс"
	@echo "  Employee.hpp     — сотрудник"
	@echo "  Teacher.hpp      — учитель"
	@echo "  Student.hpp      — ученик"
	@echo "  Classroom.hpp    — аудитория"
	@echo "  School.hpp/cpp   — школа (из прошлых семинаров)"
	@echo "  MyContainer.hpp  — коллекция (из прошлых семинаров)"
	@echo "  Makefile         — сборка: make / make run / make clean"
	@echo ""

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run structure
