#include "stamp.h"
#include "../tracking/TrackableTypes.h"

stamp::stamp(long id, std::vector<uint8_t> & marker_bits, uint8_t marker_size, std::string const & name, stamp_type const & type)
: m_id(id), m_marker_bits(marker_bits), m_marker_size(marker_size), m_type(type), Trackable(TrackableTypes::TANGIBLE, name)
{}

stamp::stamp_type stamp::type() const
{
    return m_type;
}

stamp::~stamp() = default;

/*
void stamp::draw(cv::Mat & target, std::vector<uint8_t> const & ids)
{
    if(!ids.size())
        return;

    for(auto id = ids.begin(); id != ids.end(); ++id)
    {
        if(this->id() == * id)
        {
            if(this->roi().size() > 0)
            {
                switch(this->type())
                {
                    case stamp::stamp_type::ACCEPT:
                        cv::putText(target, "ACCEPT", this->roi()[1], 1, 1, cv::Scalar(0, 0, 255));
                        break;

                    case stamp::stamp_type::REJECT:
                        cv::putText(target, "REJECT", this->roi()[1], 1, 1, cv::Scalar(0, 0, 255));
                        break;

                    case stamp::stamp_type::NOTED:
                        cv::putText(target, "NOTED", this->roi()[1], 1, 1, cv::Scalar(0, 0, 255));
                        break;
                }

                physical_object::draw(target, ids);
            }
        }
    }
}
*/

std::string const stamp::type_to_string()
{
    switch(this->m_type)
    {
        case stamp_type::ACCEPT: return "ACCEPT";
        case stamp_type::REJECT: return "REJECT";
        case stamp_type::NOTED: return "NOTED";
    }
}

long const stamp::id() const
{
    return m_id;
}

std::vector<uint8_t> & stamp::marker_bits()
{
    return m_marker_bits;
}

uint8_t stamp::marker_size()
{
    return m_marker_size;
}
