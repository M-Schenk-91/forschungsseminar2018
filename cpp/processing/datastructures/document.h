#ifndef UNTITLED1_DOCUMENT_H
#define UNTITLED1_DOCUMENT_H

#include "stamp.h"
#include "../tracking/Trackable.h"


class document : public Trackable
{
public:
    document(long id, std::vector<uint8_t> & marker_bits, uint8_t marker_size, std::string const & name, int type=-1);
    ~document() override;

    bool stamped();
    // void set_stamped();

    // const std::vector<stamp::stamp_type> & get_stamp_signatures() const;

    // void add_stamp_signature(stamp const & s);

    uint8_t const id() const;
    uint8_t marker_size();
    std::vector<uint8_t> & marker_bits();

    int type() const;

private:
    // bool m_stamped = false;
    long m_id;
    std::vector<uint8_t> m_marker_bits;
    uint8_t m_marker_size;

    // std::vector<stamp::stamp_type> m_stamp_signatures;
};


#endif //UNTITLED1_DOCUMENT_H
