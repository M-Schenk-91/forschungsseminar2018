#ifndef UNTITLED1_SMATH_H
#define UNTITLED1_SMATH_H

#include <opencv2/opencv.hpp>
#include "../util/util.h"

namespace math
{
    const float DIN_A4_FACTOR_EXPAND = -2.0f;
    const float DIN_A4_FACTOR_CORNER = -0.6f;

    template<typename _T>
    float cross(const _T & v, const _T & u)
    {
        return (float) v.cross(u);
    }

    template<typename _T>
    cv::Point2f intersection(const _T & p, const _T & q, const _T &r, const _T &s)
    {
        cv::Point2f x = r - p;
        cv::Point2f d1 = q - p;
        cv::Point2f d2 = s - r;

        float t1 = cross(x, d2) / cross(d1, d2);

        return p + d1 * t1;
    }

    template <typename _T>
    cv::Point2f transform_marker_corner_points_to_DIN_A4_sheet_corners(_T const & p, _T const & q,
                                                                       _T const & i)
    {
        return p + (i - p) * DIN_A4_FACTOR_EXPAND + (q - p) * DIN_A4_FACTOR_CORNER ;
    }

    template <typename _T>
    bool is_point_in_convex_polygon(_T const & p, std::vector<_T> const & convex_polygon)
    {
        return cv::pointPolygonTest(convex_polygon, p, false) >= 0.0;
    }

    template <typename _T1, typename _T2>
    _T1 const vector_norm(_T2 const & p)
    {
        return (_T1) (std::sqrt(p.x * p.x + p.y * p.y));
    }

    template <typename _T>
    float const dot(_T const & a, _T const & b)
    {
        return (float) a.dot(b);
    }

    template <typename _T>
    float const angle_degrees(_T const & a, _T const & b)
    {
        return (float) (std::acos(dot(a, b) /(vector_norm<float, _T>(a) * vector_norm<float, _T>(b))) * 180.0f / CV_PI);
    }

    template <typename _T>
    float const to_degrees(_T const a)
    {
        return a * 180.0 / CV_PI;
    }

    template <typename _T>
    void merge_close_points(std::vector<_T> & points, float const maximum_distance)
    {
        std::vector<_T> temp;
        std::vector<bool> checked;

        for(auto const & i : points)
            checked.push_back(false);

        for(int i = 0; i < points.size(); i++)
        {
            if (!checked[i])
            {
                int count = 1;

                cv::Point p = points[i];

                checked[i] = true;

                for (int k = i + 1; k < points.size(); k++)
                {
                    if (math::vector_norm<float, cv::Point>(points[k] - points[i]) < maximum_distance)
                    {
                        p += points[k];
                        count++;
                        checked[k] = true;
                    }
                }

                p /= count;

                temp.push_back(p);
            }
        }

        points.clear();

        for(auto const & i : temp)
            points.push_back(i);
    }

    template <typename _T>
    void approximate_hand_roi(std::vector<_T> & points, cv::Rect & aabb, _T const & hand_center, int const min_area=27000)
    {
        if(aabb.width > aabb.height)
            aabb.height = aabb.width;
        else
            aabb.width = aabb.height;

        while(aabb.area() < min_area)
        {
            aabb.height += 10;
            aabb.width += 10;
        }

        _T center(aabb.tl().x + aabb.width / 2, aabb.tl().y + aabb.height / 2);

        _T tlc = (_T) aabb.tl();
        _T blc(aabb.tl().x, aabb.tl().y + aabb.height);
        _T brc(aabb.tl().x + aabb.width, aabb.tl().y + aabb.height);
        _T trc(aabb.tl().x + aabb.width, aabb.tl().y);

        _T translation_vector = hand_center - center;

        points.push_back(tlc + translation_vector);
        points.push_back(blc + translation_vector);
        points.push_back(brc + translation_vector);
        points.push_back(trc + translation_vector);
    }
}

#endif //UNTITLED1_SMATH_H
