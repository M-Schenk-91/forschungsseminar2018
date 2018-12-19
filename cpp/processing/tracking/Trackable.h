
#ifndef MTT_TRACKABLE_H
#define MTT_TRACKABLE_H


#include <stdint-gcc.h>
#include <opencv2/opencv.hpp>
#include <vector>

class Trackable
{
public:
    Trackable(uint8_t type_id, std::string const & name);
    virtual ~Trackable();

    uint8_t const type_id() const;

    std::vector<cv::Point2f> const & roi() const;

    void draw(cv::Mat & frame, int const size) const;
    void set_roi(std::vector<cv::Point2f> const & corners, float const factor);

    void const set_center(cv::Point2f const & center);
    void const set_height(float h);
    void const set_width(float w);
    void const set_angle(float a);

    cv::Point2f const & center() const;
    float const width() const;
    float const height() const;
    float const angle() const;

    std::string const & name() const;

private:
    uint8_t m_type_id = -1;
    std::vector<cv::Point2f> m_roi;
    cv::Point2f m_center;
    float m_width;
    float m_height;
    float m_angle;
    std::string m_name;

protected:

};


#endif //MTT_TRACKABLE_H
