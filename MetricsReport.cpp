#include "MetricsReport.hpp"

#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

#include "ClassMetrics.hpp"

// Собираем заранее посчитанные метрики по каждому классу системы.
// Значения получены анализом иерархии Person -> Employee -> Teacher,
// Student, а также Classroom и School (см. task.txt, раздел 2).
static std::vector<ClassMetrics> buildSchoolMetrics() {
    return {
        {
            "Person",
            4, 0, 2, 2, 4, 0.0,
            4, 0, 0, 1, 0, 0, 1
        },
        {
            "Employee",
            3, 1, 1, 1, 5, 0.33,
            5, 2, 2, 2, 1, 0, 2
        },
        {
            "Teacher",
            5, 2, 0, 3, 7, 0.40,
            7, 4, 2, 3, 2, 0, 3
        },
        {
            "Student",
            4, 1, 0, 2, 5, 0.25,
            5, 1, 2, 1, 0, 0, 1
        },
        {
            "Classroom",
            2, 0, 0, 1, 2, 0.0,
            2, 0, 0, 1, 0, 0, 1
        },
        {
            "School",
            3, 0, 0, 2, 3, 0.67,
            3, 0, 0, 3, 0, 0, 3
        }
    };
}

// Выводит таблицу метрик CK для каждого класса.
static void printClassMetrics(const std::vector<ClassMetrics>& classes) {
    std::cout << std::fixed << std::setprecision(2);

    std::cout << "\n=== Метрики по классам (CK / Lorenz-Kidd) ===\n\n";
    std::cout << std::left
              << std::setw(12) << "Класс"
              << std::setw(6) << "WMC"
              << std::setw(6) << "DIT"
              << std::setw(6) << "NOC"
              << std::setw(6) << "CBO"
              << std::setw(6) << "RFC"
              << "LCOM\n";
    std::cout << std::string(52, '-') << '\n';

    for (const ClassMetrics& cls : classes) {
        std::cout << std::setw(12) << cls.name
                  << std::setw(6) << cls.wmc
                  << std::setw(6) << cls.dit
                  << std::setw(6) << cls.noc
                  << std::setw(6) << cls.cbo
                  << std::setw(6) << cls.rfc
                  << cls.lcom << '\n';
    }
}

// Считает системные метрики MOOD (Абреу) по всем классам.
static void printMoodMetrics(const std::vector<ClassMetrics>& classes) {
    const int classCount = static_cast<int>(classes.size());
    double mifSum = 0.0;
    double ahfSum = 0.0;
    double pofSum = 0.0;
    int totalMethods = 0;
    int totalHiddenMethods = 0;
    int totalAttributes = 0;
    int totalHiddenAttributes = 0;

    for (const ClassMetrics& cls : classes) {
        if (cls.totalMethods > 0) {
            mifSum += static_cast<double>(cls.inheritedMethods) / cls.totalMethods;
            pofSum += static_cast<double>(cls.overriddenMethods) / cls.totalMethods;
        }
        if (cls.totalAttributes > 0) {
            ahfSum += static_cast<double>(cls.inheritedAttributes) / cls.totalAttributes;
        }

        totalMethods += cls.totalMethods;
        totalHiddenMethods += cls.hiddenMethods;
        totalAttributes += cls.totalAttributes;
        totalHiddenAttributes += cls.hiddenAttributes;
    }

    const double mif = mifSum / classCount;
    const double ahf = ahfSum / classCount;
    const double pof = pofSum / classCount;
    const double mhf = totalMethods > 0
        ? static_cast<double>(totalHiddenMethods) / totalMethods
        : 0.0;
    const double chf = totalAttributes > 0
        ? static_cast<double>(totalHiddenAttributes) / totalAttributes
        : 0.0;

    // Связи между классами (наследование + ассоциации/агрегация/композиция).
    const int actualCouplings = 6;
    const int possibleCouplings = classCount * (classCount - 1) / 2;
    const double cof = static_cast<double>(actualCouplings) / possibleCouplings;

    std::cout << "\n=== Системные метрики MOOD (Абреу) ===\n\n";
    std::cout << "MIF (наследование методов):  " << mif << "  — доля унаследованных методов\n";
    std::cout << "AHF (наследование атрибутов): " << ahf << "  — доля унаследованных атрибутов\n";
    std::cout << "POF (полиморфизм):           " << pof << "  — доля переопределённых методов\n";
    std::cout << "COF (сцепление системы):    " << cof << "  — "
              << actualCouplings << " из " << possibleCouplings << " возможных связей\n";
    std::cout << "MHF (сокрытие методов):      " << mhf << '\n';
    std::cout << "CHF (сокрытие атрибутов):    " << chf << '\n';
}

// Краткий анализ: сравниваем значения с рекомендациями из task.txt.
static void printAnalysis(const std::vector<ClassMetrics>& classes) {
    int maxDit = 0;
    int maxCbo = 0;
    int maxRfc = 0;
    int maxWmc = 0;

    for (const ClassMetrics& cls : classes) {
        maxDit = std::max(maxDit, cls.dit);
        maxCbo = std::max(maxCbo, cls.cbo);
        maxRfc = std::max(maxRfc, cls.rfc);
        maxWmc = std::max(maxWmc, cls.wmc);
    }

    std::cout << "\n=== Анализ архитектуры «Школа» ===\n\n";
    std::cout << "DIT (макс.): " << maxDit << " — ";
    std::cout << (maxDit <= 5 ? "в норме (<= 5)\n" : "слишком глубокое наследование\n");

    std::cout << "CBO (макс.): " << maxCbo << " — ";
    std::cout << (maxCbo <= 15 ? "слабое сцепление, хорошо\n" : "высокая связанность\n");

    std::cout << "RFC (макс.): " << maxRfc << " — ";
    std::cout << (maxRfc <= 50 ? "классы простые для тестирования\n" : "слишком много реакций\n");

    std::cout << "WMC (макс.): " << maxWmc << " — ";
    std::cout << (maxWmc <= 20 ? "низкая сложность классов\n" : "класс перегружен методами\n");

    std::cout << "\nВывод: иерархия Person -> Employee -> Teacher неглубокая,\n";
    std::cout << "классы небольшие, полиморфизм используется через printInfo()\n";
    std::cout << "и primaryResponsibility(). Связи School-Classroom (композиция)\n";
    std::cout << "и Student-Teacher (ассоциация) умеренные.\n";
}

// Пояснения к каждому классу — как в примере с библиотекой из задания.
static void printExplanations() {
    std::cout << "\n=== Пояснения к расчёту ===\n\n";

    std::cout << "Person: WMC=4 (dtor, getName, 2 чистых virtual), NOC=2 (Employee, Student).\n";
    std::cout << "Employee: WMC=3, DIT=1, переопределяет 2 метода Person, NOC=1 (Teacher).\n";
    std::cout << "Teacher: WMC=5 (+ teach, getSubject, operator==), DIT=2, CBO=3 (Employee, School, Student).\n";
    std::cout << "Student: WMC=4 (+ study, setAdvisor), связан с Person и Teacher.\n";
    std::cout << "Classroom: WMC=2 (open, dtor), используется только в School (композиция).\n";
    std::cout << "School: WMC=3, CBO=2 (Classroom, Teacher), агрегирует учителей.\n";
}

void runMetricsReport() {
    std::cout << "=== Семинар 7-8: Метрики ООП ===\n";
    std::cout << "Предметная область: Школа\n";

    const std::vector<ClassMetrics> classes = buildSchoolMetrics();

    std::cout << "\nКлассы системы (" << classes.size() << "): Person, Employee, Teacher,\n";
    std::cout << "Student, Classroom, School.\n";

    printClassMetrics(classes);
    printMoodMetrics(classes);
    printAnalysis(classes);
    printExplanations();
}
