#ifndef UNTITLED1_STAMP_H
#define UNTITLED1_STAMP_H

#include <vector>
#include <opencv2/opencv.hpp>
#include "../tracking/Trackable.h"

class stamp : public Trackable
{
public:
    enum stamp_type
    {
        ACCEPT,
        REJECT,
        VERIFY,
        RETURN,
        NOTED,
        REMOVE
    };

    stamp(long id, std::vector<uint8_t> & marker_bits, uint8_t marker_size, std::string const & name, stamp_type const & type);
    ~stamp();

    stamp_type type() const;

    std::string const type_to_string();

    long const id() const;
    std::vector<uint8_t> & marker_bits();
    uint8_t marker_size();

private:
    stamp_type m_type;
    long m_id;
    std::vector<uint8_t> m_marker_bits;
    uint8_t m_marker_size;
};


#endif //UNTITLED1_STAMP_H
