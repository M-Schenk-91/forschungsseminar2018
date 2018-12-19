#ifndef MTT_STIME_H
#define MTT_STIME_H

#include <chrono>

class Time
{
public:
    static double time()
    {
        return std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::system_clock::now() -
                m_epoch).count() / 1000000000.0;
    }

    static void set_time_delta(double delta)
    {
        Time::m_time_delta = delta;
    }

    static double time_delta()
    {
        return m_time_delta;
    }

private:
    static double m_time_delta;
    static std::chrono::system_clock::time_point m_epoch;
};

double Time::m_time_delta = 0.0;
std::chrono::system_clock::time_point Time::m_epoch = std::chrono::system_clock::now();

#endif //MTT_STIME_H
