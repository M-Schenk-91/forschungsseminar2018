#ifndef UNTITLED1_UTIL_H

#define UNTITLED1_UTIL_H

#include <opencv2/opencv.hpp>
#include "../lib/surface.h"

namespace util
{
    template <typename _T>
    void print(_T msg)
    {
        std::cout << msg << std::endl;
    }
}


#endif //UNTITLED1_UTIL_H
