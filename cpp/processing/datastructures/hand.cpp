
#include "hand.h"
#include "../tracking/TrackableTypes.h"

hand::hand(int id, cv::Point const & hand_center, std::vector<cv::Point> const & finger_tips, std::vector<cv::Point> const & comple_hull) :
        m_id(id), m_hand_center(hand_center), m_finger_tips(finger_tips), m_complete_hull(comple_hull), Trackable(TrackableTypes::HAND, "hand")
{}

hand::~hand() = default;

cv::Point const & hand::hand_center() const
{
    return m_hand_center;
}

std::vector<cv::Point> const & hand::finger_tips() const
{
    return m_finger_tips;
}

std::vector<cv::Point> const & hand::complete_hull() const
{
    return m_complete_hull;
}

int const hand::id() const
{
    return m_id;
}


void const hand::set_id(int const id)
{
    m_id = id;
}