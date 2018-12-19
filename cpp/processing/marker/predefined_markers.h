#ifndef UNTITLED1_PREDEFINED_MARKERS_H
#define UNTITLED1_PREDEFINED_MARKERS_H

#include <stdint-gcc.h>
#include <vector>

namespace proc::mkr
{
    std::vector<std::vector<uint8_t >> predefined_markers_6x6 =
    {
        std::vector<uint8_t >
        {
            1, 1, 0, 0, 1, 1,
            1, 1, 0, 0, 1, 1,
            0, 1, 1, 0, 0, 1,
            0, 0, 1, 1, 1, 1,
            1, 0, 0, 1, 0, 1,
            1, 0, 0, 1, 1, 0
        },

        std::vector<uint8_t >
        {
            1, 0, 0, 1, 0, 1,
            0, 1, 0, 0, 1, 1,
            0, 1, 1, 0, 0, 1,
            1, 1, 1, 0, 0, 0,
            0, 1, 0, 1, 1, 1,
            0, 0, 0, 0, 1, 0
        }
    };

    std::vector<std::vector<uint8_t >> predefined_markers_4x4 =
    {
        std::vector<uint8_t >
        {
            1, 1, 0, 1,
            1, 0, 1, 1,
            1, 0, 1, 1,
            1, 1, 0, 1
        },

        std::vector<uint8_t>
        {
            1, 1, 1, 1,
            0, 0, 1, 1,
            1, 1, 0, 0,
            1, 1, 1, 1
        },

        std::vector<uint8_t>
        {
            1, 0, 0, 1,
            0, 1, 1, 0,
            0, 1, 1, 0,
            1, 0, 0, 1
        },

        std::vector<uint8_t>
        {
            1, 1, 0, 0,
            0, 1, 0, 0,
            0, 0, 0, 1,
            0, 0, 1, 1
        }
    };
}

#endif //UNTITLED1_PREDEFINED_MARKERS_H
