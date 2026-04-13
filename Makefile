CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra

# Имя исполняемого файла
TARGET   = school

# Все .cpp файлы в текущей директории
SRCS     = main.cpp School.cpp
OBJS     = $(SRCS:.cpp=.o)

# Цель по умолчанию — собрать проект
all: $(TARGET)

# Линковка объектных файлов в исполняемый
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Компиляция каждого .cpp в .o
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Очистка скомпилированных файлов
clean:
	rm -f $(OBJS) $(TARGET)
