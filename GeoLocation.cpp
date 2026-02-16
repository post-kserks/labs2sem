#include "GeoLocation.h"
#include <cmath>
#include <iomanip>
#include <sstream>

// Константы
const double PI = 3.14159265358979323846;
const double EARTH_RADIUS_KM = 6371.0;

// Вспомогательная функция для перевода градусов в радианы
double toRadians(double degrees) {
    return degrees * PI / 180.0;
}

GeoLocation::GeoLocation() : latitude(0.0), longitude(0.0) {}

GeoLocation::GeoLocation(double lat, double lon) : latitude(lat), longitude(lon) {
    if (!isValid()) {
        // В учебных целях просто выведем предупреждение, если координаты выходят за границы
        // Хотя в реальном проекте здесь лучше выбросить исключение
    }
}

double GeoLocation::getLatitude() const { return latitude; }
void GeoLocation::setLatitude(double lat) { latitude = lat; }

double GeoLocation::getLongitude() const { return longitude; }
void GeoLocation::setLongitude(double lon) { longitude = lon; }

bool GeoLocation::isValid() const {
    return (latitude >= -90.0 && latitude <= 90.0) && 
           (longitude >= -180.0 && longitude <= 180.0);
}

double GeoLocation::distanceTo(const GeoLocation& other) const {
    // Формула Хаверсина для вычисления расстояния по поверхности сферы
    double lat1 = toRadians(latitude);
    double lon1 = toRadians(longitude);
    double lat2 = toRadians(other.latitude);
    double lon2 = toRadians(other.longitude);

    double dLat = lat2 - lat1;
    double dLon = lon2 - lon1;

    double a = std::pow(std::sin(dLat / 2), 2) +
               std::cos(lat1) * std::cos(lat2) * std::pow(std::sin(dLon / 2), 2);
    double c = 2 * std::atan2(std::sqrt(a), std::sqrt(1 - a));

    return EARTH_RADIUS_KM * c;
}

std::string GeoLocation::hemisphere() const {
    std::string result = "";
    result += (latitude >= 0) ? "North" : "South";
    result += "-";
    result += (longitude >= 0) ? "East" : "West";
    return result;
}

bool GeoLocation::isSameHemisphere(const GeoLocation& other) const {
    // Проверяем только широту для простоты (северное/южное)
    return (latitude >= 0) == (other.latitude >= 0);
}

std::string GeoLocation::toString() const {
    std::stringstream ss;
    ss << std::fixed << std::setprecision(6) << "(" << latitude << ", " << longitude << ")";
    return ss.str();
}

void GeoLocation::display() const {
    std::cout << "GeoLocation [Lat: " << latitude << ", Lon: " << longitude 
              << "] Hemisphere: " << hemisphere() << std::endl;
}

bool GeoLocation::operator==(const GeoLocation& other) const {
    // Используем небольшую погрешность для сравнения double
    const double eps = 1e-9;
    return std::abs(latitude - other.latitude) < eps && 
           std::abs(longitude - other.longitude) < eps;
}

bool GeoLocation::operator!=(const GeoLocation& other) const {
    return !(*this == other);
}

std::ostream& operator<<(std::ostream& os, const GeoLocation& gl) {
    os << gl.toString();
    return os;
}

double GeoLocation::fromDMS(double degrees, double minutes, double seconds, char direction) {
    double decimal = degrees + (minutes / 60.0) + (seconds / 3600.0);
    if (direction == 'S' || direction == 'W' || direction == 's' || direction == 'w') {
        decimal *= -1.0;
    }
    return decimal;
}
