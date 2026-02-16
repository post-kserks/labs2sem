#ifndef GEOLOCATION_H
#define GEOLOCATION_H

#include <iostream>
#include <string>

/**
 * Класс GeoLocation представляет географические координаты (широта и долгота).
 */
class GeoLocation {
private:
    double latitude;  // Широта (от -90 до 90)
    double longitude; // Долгота (от -180 до 180)

public:
    // 1.2. Конструкторы
    GeoLocation(); // По умолчанию (0, 0)
    GeoLocation(double lat, double lon); // С параметрами

    // 1.3. Get и set методы
    double getLatitude() const;
    void setLatitude(double lat);
    double getLongitude() const;
    void setLongitude(double lon);

    // 1.4. Публичные методы (5-6 методов)
    
    // Вычисляет расстояние до другой точки по формуле Хаверсина (в км)
    double distanceTo(const GeoLocation& other) const;
    
    // Возвращает строку с описанием полушарий (например, "North-East")
    std::string hemisphere() const;
    
    // Проверяет корректность координат
    bool isValid() const;
    
    // Проверяет, находятся ли точки в одном полушарии (северное/южное)
    bool isSameHemisphere(const GeoLocation& other) const;
    
    // Возвращает строковое представление координат
    std::string toString() const;

    // 1.7. Метод для вывода состояния
    void display() const;

    // 1.5. Перегрузка операторов
    bool operator==(const GeoLocation& other) const;
    bool operator!=(const GeoLocation& other) const;
    friend std::ostream& operator<<(std::ostream& os, const GeoLocation& gl);

    // 1.6. Статический метод
    // Преобразует градусы, минуты, секунды и направление (N, S, E, W) в десятичный формат
    static double fromDMS(double degrees, double minutes, double seconds, char direction);
};

#endif // GEOLOCATION_H
