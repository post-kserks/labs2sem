#ifndef LANDMARK_H
#define LANDMARK_H

#include "GeoLocation.h"
#include <string>

/**
 * Класс Landmark представляет географический объект (ориентир),
 * который имеет название и координаты.
 * Наследуется от GeoLocation для переиспользования существующего функционала.
 */
class Landmark : public GeoLocation {
private:
    std::string name;

public:
    Landmark(const std::string& name, double lat, double lon);

    const std::string& getName() const;
    void setName(const std::string& newName);

    // Переопределённый оператор вывода:
    // печатает название ориентира и его координаты.
    friend std::ostream& operator<<(std::ostream& os, const Landmark& lm);
};

/**
 * Функция вывода информации о маршруте между двумя точками.
 * Печатает начальную и конечную точки и расстояние между ними.
 */
void printRoute(GeoLocation from, GeoLocation to);

#endif // LANDMARK_H

