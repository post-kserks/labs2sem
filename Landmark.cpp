#include "Landmark.h"
#include <iostream>
#include <iomanip>

Landmark::Landmark(const std::string& name, double lat, double lon)
    : GeoLocation(lat, lon), name(name) {}

const std::string& Landmark::getName() const {
    return name;
}

void Landmark::setName(const std::string& newName) {
    name = newName;
}

std::ostream& operator<<(std::ostream& os, const Landmark& lm) {
    os << lm.name << ": " << static_cast<const GeoLocation&>(lm);
    return os;
}

void printRoute(GeoLocation from, GeoLocation to) {
    std::cout << "\n--- Маршрут ---" << std::endl;
    std::cout << "Начальная точка: " << from << " (" << from.hemisphere() << ")" << std::endl;
    std::cout << "Конечная точка: " << to << " (" << to.hemisphere() << ")" << std::endl;
    std::cout << "Расстояние: " << std::fixed << std::setprecision(2)
              << from.distanceTo(to) << " км" << std::endl;
}

