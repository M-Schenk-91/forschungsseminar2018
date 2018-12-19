#include <opencv2/core/types.hpp>
#include "document.h"
#include "../tracking/TrackableTypes.h"

document::document(long id, std::vector<uint8_t> & marker_bits, uint8_t marker_size, std::string const & name, int type) :
m_id(id), m_marker_bits(marker_bits), m_marker_size(marker_size), Trackable(TrackableTypes::PHYSICAL_DOCUMENT, name)
{}

document::~document() = default;

/*
bool document::stamped()
{
    return false;
}

void document::set_stamped()
{
    this->m_stamped = true;
}

const std::vector<stamp::stamp_type> & document::get_stamp_signatures() const {
    return m_stamp_signatures;
}6A

void document::add_stamp_signature(stamp const & s)
{
    for(auto sts = m_stamp_signatures.begin(); sts != m_stamp_signatures.end(); ++ sts)
    {
        if(s.type() == * sts)
            return;
    }

    m_stamp_signatures.push_back(s.type());
}
*/

uint8_t const document::id() const
{
    return this->m_id;
}

uint8_t document::marker_size()
{
    return m_marker_size;
}

std::vector<uint8_t> & document::marker_bits()
{
    return m_marker_bits;
}

int document::type() const
{
    return -1;
}