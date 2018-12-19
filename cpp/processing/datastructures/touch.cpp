
#include "touch.h"
#include "../tracking/TrackableTypes.h"

touch::touch(uint8_t id, cv::Point2f const & finger_tip, float area) :
       m_id(id), m_finger_tip(finger_tip), m_area(area), Trackable(TrackableTypes::TOUCH, "TOUCH")
{}

touch::~touch() = default;

cv::Point2f const &touch::finger_tip() const
{
    return m_finger_tip;
}

uint8_t const touch::id() const
{
    return m_id;
}

float const touch::area() const
{
    return m_area;
}
