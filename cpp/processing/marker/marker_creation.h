#ifndef UNTITLED1_MARKER_CREATION_H
#define UNTITLED1_MARKER_CREATION_H

#include <iostream>
#include <opencv2/opencv.hpp>
#include <stdint-gcc.h>
#include <opencv2/aruco/dictionary.hpp>
#include "../datastructures/document.h"

namespace proc::mkr
{
    template <typename _T>
    cv::Ptr<cv::aruco::Dictionary> marker_dictionary_from_physical_object_list(std::vector<_T> & objects)
    {
        cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::generateCustomDictionary(objects.size(), objects[0].marker_size());

        dictionary->bytesList = cv::Mat();

        for(auto o = objects.begin(); o != objects.end(); ++o)
        {
            cv::Mat marker_bits = cv::Mat(o->marker_size(), o->marker_size(), CV_8UC1, o->marker_bits().data());
            cv::Mat marker_compressed = cv::aruco::Dictionary::getByteListFromBits(marker_bits);

            dictionary->bytesList.push_back(marker_compressed);
        }

        return dictionary;
    }
}

#endif //UNTITLED1_MARKER_CREATION_H
