
#include "Trackable.h"
#include "TrackableTypes.h"
#include "../datastructures/document.h"
#include "../datastructures/stamp.h"
#include "../datastructures/hand.h"
#include "../datastructures/touch.h"

#include "../../math/smath.h"

Trackable::Trackable(uint8_t type_id, std::string const & name) : m_type_id(type_id), m_name(name)
{}

Trackable::~Trackable() = default;

uint8_t const Trackable::type_id() const
{
    return this->m_type_id;
}

std::vector<cv::Point2f> const & Trackable::roi() const
{
    return this->m_roi;
}

void Trackable::draw(cv::Mat & target, int const size) const
{
    switch(this->m_type_id)
    {
        case TrackableTypes::PHYSICAL_DOCUMENT:
        {
            for(auto p = m_roi.begin(); p != m_roi.end(); ++p)
                cv::circle(target, * p / size, 5, cv::Scalar(0, 0, 255), -1);
        }
        break;

        case TrackableTypes::TANGIBLE:
        {
            if(this->m_roi.size() > 0)
            {
                auto const & s = (* (stamp *) this);

                switch(s.type())
                {
                    case stamp::stamp_type::ACCEPT:
                        cv::putText(target, "ACCEPT", this->roi()[1] / size, 1, 1, cv::Scalar(0, 0, 255));
                        break;

                    case stamp::stamp_type::REJECT:
                        cv::putText(target, "REJECT", this->roi()[1] / size, 1, 1, cv::Scalar(0, 0, 255));
                        break;

                    case stamp::stamp_type::NOTED:
                        cv::putText(target, "NOTED", this->roi()[1] / size, 1, 1, cv::Scalar(0, 0, 255));
                        break;
                }
            }

            for(auto p = m_roi.begin(); p != m_roi.end(); ++p)
                cv::circle(target, * p / size, 5, cv::Scalar(0, 0, 255), -1);
        }
        break;

        case TrackableTypes::HAND:
        {
            auto const & h = (* (hand *) this);

            if(h.roi().size() == 4)
            {
                for(int i = 0; i < 4; i++)
                    cv::line(target, this->roi()[i] / size, this->roi()[(i + 1) % 4] / size, cv::Scalar(255, 0, 0));

                for(auto const & p : h.finger_tips())
                    cv::circle(target, p, 5, cv::Scalar(0, 0, 255), -1);

                cv::circle(target, h.hand_center(), 5, cv::Scalar(0, 255, 0), -1);
            }
        }
        break;

        case TrackableTypes::TOUCH:
        {
            auto const & t = (* (touch *) this);

            cv::circle(target, t.center() / size, 5, cv::Scalar(255, 0, 0), -1);

            cv::RotatedRect rr(t.center(), cv::Size(t.width(), t.height()), t.angle());

            cv::Point2f pts[4];

            rr.points(pts);

            for(int i = 0; i < 4; i++)
                cv::circle(target, pts[i] / size, 5, cv::Scalar(0, 0, 255), -1);
        }
        break;
    }
}

void Trackable::set_roi(std::vector<cv::Point2f> const & corners, float const factor)
{
    switch(this->m_type_id)
    {
        case TrackableTypes::PHYSICAL_DOCUMENT:
        {
            m_roi.clear();

            cv::Point2f intersection = math::intersection(corners[0], corners[2], corners[1], corners[3]);

            intersection.x *= factor;
            intersection.y *= factor;

            m_roi = std::vector<cv::Point2f>
            {
                math::transform_marker_corner_points_to_DIN_A4_sheet_corners(cv::Point2f(corners[0].x * factor, corners[0].y * factor), cv::Point2f(corners[3].x * factor, corners[3].y * factor), intersection),
                math::transform_marker_corner_points_to_DIN_A4_sheet_corners(cv::Point2f(corners[1].x * factor, corners[1].y * factor), cv::Point2f(corners[2].x * factor, corners[2].y * factor), intersection),
                math::transform_marker_corner_points_to_DIN_A4_sheet_corners(cv::Point2f(corners[2].x * factor, corners[2].y * factor), cv::Point2f(corners[1].x * factor, corners[1].y * factor), intersection),
                math::transform_marker_corner_points_to_DIN_A4_sheet_corners(cv::Point2f(corners[3].x * factor, corners[3].y * factor), cv::Point2f(corners[0].x * factor, corners[0].y * factor), intersection)
            };

            this->m_center = math::intersection(this->roi()[2], this->roi()[0], this->roi()[3], this->roi()[1]);
            this->m_width = math::vector_norm<float, cv::Point2f>(this->roi()[1] - this->roi()[0]);
            this->m_height = math::vector_norm<float, cv::Point2f>(this->roi()[3] - this->roi()[0]);
            this->m_angle = (this->roi()[0].x > this->roi()[1].x) ? 360.0f - math::angle_degrees(this->roi()[3]- this->roi()[0], cv::Point2f(1, 0)) : math::angle_degrees(this->roi()[3] - this->roi()[0], cv::Point2f(1, 0));
        }
        break;

        case TrackableTypes::TANGIBLE:
        case TrackableTypes::HAND:
        {
            m_roi.clear();

            for(auto p = corners.rbegin(); p != corners.rend(); ++p)
                m_roi.push_back(cv::Point(p->x * factor, p->y * factor));

            this->m_center = math::intersection(this->roi()[2], this->roi()[0], this->roi()[3], this->roi()[1]);
            this->m_width = math::vector_norm<float, cv::Point2f>(this->roi()[1] - this->roi()[0]);
            this->m_height = math::vector_norm<float, cv::Point2f>(this->roi()[3] - this->roi()[0]);
            this->m_angle = -((this->roi()[0].x > this->roi()[1].x) ? 360.0f - math::angle_degrees(this->roi()[3]- this->roi()[0], cv::Point2f(1, 0)) : math::angle_degrees(this->roi()[3] - this->roi()[0], cv::Point2f(1, 0)));
        }

        break;

        case TrackableTypes::TOUCH:
        {
            m_roi.clear();

            for(auto p = corners.begin(); p != corners.end(); ++p)
                m_roi.push_back(cv::Point(p->x * factor, p->y * factor));
        }
        break;
    }
}

void const Trackable::set_center(cv::Point2f const & center)
{
    m_center = center;
}

void const Trackable::set_height(float h)
{
    m_height = h;
}

void const Trackable::set_width(float w)
{
    m_width = w;
}

void const Trackable::set_angle(float a)
{
    m_angle = a;
}

cv::Point2f const & Trackable::center() const
{
    return m_center;
}

float const Trackable::width() const
{
    return m_width;
}

float const Trackable::height() const
{
    return m_height;
}

float const Trackable::angle() const
{
    return m_angle;
}

std::string const & Trackable::name() const {
    return m_name;
}
