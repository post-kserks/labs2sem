#include "GeoLocation.h"
#include <iostream>

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

    return 0;
}
