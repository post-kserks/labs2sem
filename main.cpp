#include "GeoLocation.h"
#include "Landmark.h"
#include <iostream>

// Полиморфная функция (перегруженная для базового и производного классов)
void printLocationInfo(const GeoLocation& location) {
    std::cout << "Точка: " << location << std::endl;
}

void printLocationInfo(const Landmark& landmark) {
    std::cout << "Ориентир: " << landmark << std::endl;
}

// Функция move: работает с базовым классом (перемещение).
// Принимает ссылку на базовый класс, поэтому не знает о классах-потомках.
void move(GeoLocation& loc, double newLat, double newLon) {
    loc.setLatitude(newLat);
    loc.setLongitude(newLon);
    std::cout << "Результат перемещения: " << loc << std::endl;
}

int main() {
    // 1. Создание объектов через конструктор по умолчанию
    GeoLocation moscow;
    moscow.setLatitude(55.7558);
    moscow.setLongitude(37.6173);

    // 2. Создание объекта через конструктор с параметрами (Санкт-Петербург)
    GeoLocation stPetersburg(59.9343, 30.3351);

    // 3. Использование статического метода fromDMS
    // Координаты Эвереста: 27°59′17″ N, 86°55′31″ E
    double everestLat = GeoLocation::fromDMS(27, 59, 17, 'N');
    double everestLon = GeoLocation::fromDMS(86, 55, 31, 'E');
    GeoLocation everest(everestLat, everestLon);

    // 4. Демонстрация вывода состояния (display)
    std::cout << "--- Состояние объектов ---" << std::endl;
    std::cout << "Москва: "; moscow.display();
    std::cout << "Санкт-Петербург: "; stPetersburg.display();
    std::cout << "Эверест: "; everest.display();

    // 5. Использование перегруженного оператора <<
    std::cout << "\nВывод через оператор <<: " << moscow << std::endl;

    // 6. Вычисление расстояния (distanceTo)
    double dist = moscow.distanceTo(stPetersburg);
    std::cout << "\nРасстояние от Москвы до Санкт-Петербурга: " << dist << " км" << std::endl;

    // 7. Использование других публичных методов
    std::cout << "Эверест находится в полушарии: " << everest.hemisphere() << std::endl;
    
    if (moscow.isSameHemisphere(stPetersburg)) {
        std::cout << "Москва и Санкт-Петербург в одном широтом полушарии." << std::endl;
    }

    // 8. Сравнение объектов (оператор ==)
    GeoLocation anotherMoscow(55.7558, 37.6173);
    if (moscow == anotherMoscow) {
        std::cout << "\nОператор ==: Объекты moscow и anotherMoscow идентичны." << std::endl;
    }

    if (moscow != stPetersburg) {
        std::cout << "Оператор !=: Москва и Санкт-Петербург — разные точки." << std::endl;
    }

    // 9. Работа с расширенным классом Landmark
    Landmark redSquare("Красная площадь", 55.7539, 37.6208);
    Landmark hermitage("Эрмитаж", 59.9398, 30.3146);

    std::cout << "\n--- Ориентиры ---" << std::endl;
    std::cout << redSquare << std::endl;
    std::cout << hermitage << std::endl;

    // 10. Демонстрация полиморфной функции
    std::cout << "\n--- Полиморфная функция printLocationInfo ---" << std::endl;
    printLocationInfo(moscow);      // базовый класс
    printLocationInfo(redSquare);   // расширенный класс

    // 11. Демонстрация функции маршрута
    std::cout << "\n--- Функция printRoute ---" << std::endl;
    printRoute(moscow, stPetersburg);
    printRoute(redSquare, hermitage);

    // 12. Демонстрация функции move (работает с базовым классом)
    std::cout << "\n--- Функция move ---" << std::endl;
    std::cout << "До перемещения (базовый класс): " << moscow << std::endl;
    move(moscow, 56.0, 38.0);
    
    // Передача объекта-наследника в функцию, принимающую ссылку на базовый класс
    // Объекту-наследнику изменят координаты через методы базового класса
    std::cout << "\nДо перемещения (наследник Landmark): " << redSquare << std::endl;
    move(redSquare, 55.7500, 37.6100);
    std::cout << "После вызова move (свойства наследника сохранены): " << redSquare << std::endl;

    return 0;
}
