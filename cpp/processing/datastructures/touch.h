
#ifndef MTT_TOUCH_H
#define MTT_TOUCH_H


#include "../tracking/Trackable.h"

class touch : public Trackable
{
public:
    touch(uint8_t id, cv::Point2f const & finger_tip, float area);
    ~touch();

    cv::Point2f const & finger_tip() const;
    uint8_t const id() const;
    float const area() const;

private:
    cv::Point2f m_finger_tip;
    uint8_t m_id;
    float m_area;

};


#endif //MTT_TOUCH_H
