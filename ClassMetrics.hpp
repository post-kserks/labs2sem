#ifndef CLASS_METRICS_HPP
#define CLASS_METRICS_HPP

#include <string>

// Данные по одному классу для расчёта метрик CK и MOOD.
struct ClassMetrics {
    std::string name; // имя класса

    // Метрики Чидамбера-Кемерера (на класс)
    int wmc = 0;  // Weighted Methods per Class — число методов
    int dit = 0;  // Depth of Inheritance Tree — глубина наследования
    int noc = 0;  // Number of Children — число прямых наследников
    int cbo = 0;  // Coupling Between Objects — число связанных классов
    int rfc = 0;  // Response For a Class — методы, доступные при вызове
    double lcom = 0.0; // Lack of Cohesion of Methods

    // Дополнительные данные для метрик Абреу (MOOD)
    int totalMethods = 0;      // всего методов (с учётом унаследованных)
    int inheritedMethods = 0;  // унаследованных методов
    int overriddenMethods = 0; // переопределённых методов
    int totalAttributes = 0;   // всего атрибутов
    int inheritedAttributes = 0; // унаследованных атрибутов
    int hiddenMethods = 0;     // private/protected методы
    int hiddenAttributes = 0;  // private/protected атрибуты
};

#endif
