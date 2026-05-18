CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17

TARGET = school_app
SRCS = main.cpp MetricsReport.cpp
OBJS = $(SRCS:.cpp=.o)

HEADERS = ClassMetrics.hpp MetricsReport.hpp \
          Person.hpp Employee.hpp Teacher.hpp Student.hpp \
          Classroom.hpp School.hpp

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Показать структуру проекта лабораторной
structure:
	@echo "Структура проекта (семинар 7-8 — метрики ООП):"
	@echo ""
	@echo "  ClassMetrics.hpp   — структура данных метрик одного класса"
	@echo "  MetricsReport.hpp  — объявление функции отчёта"
	@echo "  MetricsReport.cpp  — расчёт и вывод метрик"
	@echo "  main.cpp           — точка входа"
	@echo ""
	@echo "  Классы предметной области (из прошлых семинаров):"
	@echo "  Person.hpp, Employee.hpp, Teacher.hpp, Student.hpp"
	@echo "  Classroom.hpp, School.hpp, School.cpp"
	@echo ""
	@echo "  Makefile — сборка: make / make run / make clean / make structure"
	@echo ""

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run structure
