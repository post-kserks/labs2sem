# Makefile для сборки статической библиотеки и демо-приложения

# Компилятор и флаги
CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++11
AR = ar
ARFLAGS = rcs

# Имена файлов
LIB_NAME = libgeolocation.a
EXE_NAME = demo
SRCS_LIB = GeoLocation.cpp
OBJS_LIB = $(SRCS_LIB:.cpp=.o)
SRCS_EXE = main.cpp

# Цель по умолчанию
all: $(EXE_NAME)

# Сборка библиотеки
$(LIB_NAME): $(OBJS_LIB)
	$(AR) $(ARFLAGS) $@ $^

# Компиляция объектных файлов библиотеки
%.o: %.cpp GeoLocation.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Сборка исполняемого файла
$(EXE_NAME): $(SRCS_EXE) $(LIB_NAME)
	$(CXX) $(CXXFLAGS) $(SRCS_EXE) -L. -lgeolocation -o $@

# Очистка
clean:
	rm -f $(OBJS_LIB) $(LIB_NAME) $(EXE_NAME)

# Запуск
run: all
	./$(EXE_NAME)

.PHONY: all clean run
