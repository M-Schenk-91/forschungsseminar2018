
#ifndef MTT_HAND_H
#define MTT_HAND_H


#include "../tracking/Trackable.h"
#include <vector>

class hand : public Trackable
{

public:
    hand(int id, cv::Point const & hand_center, std::vector<cv::Point> const & finger_tips, std::vector<cv::Point> const & comple_hull);
    ~hand();

    cv::Point const & hand_center() const;
    std::vector<cv::Point> const & finger_tips() const;
    std::vector<cv::Point> const & complete_hull() const;

    int const id() const;
    void const set_id(int const id);

private:
    cv::Point m_hand_center;
    std::vector<cv::Point> m_finger_tips;
    std::vector<cv::Point>m_complete_hull;
    int m_id;
};


#endif //MTT_HAND_H
