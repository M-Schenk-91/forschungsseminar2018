#ifndef MTT_MESSAGING_HANDLER_H
#define MTT_MESSAGING_HANDLER_H

#include "../processing/datastructures/document.h"
#include "../processing/datastructures/stamp.h"
#include "../processing/datastructures/hand.h"
#include "../processing/datastructures/touch.h"
#include "../processing/tracking/TrackableTypes.h"
#include "../util/util.h"

#include <TuioServer.h>

class MessagingHandler
{

public:
    MessagingHandler();
    ~MessagingHandler();

    void send_message(std::vector<std::unique_ptr<Trackable>> const & trackables, bool threaded = false);

private:
    TUIO2::OscSender * udp_sender = nullptr;
    TUIO2::TuioServer * server = nullptr;

    std::map<int, std::map<int, TUIO2::TuioObject *>> type_id_2_objects_map_with_object_id_2_object; // WTF that name

    void _update_tracked_objects(std::vector<std::unique_ptr<Trackable>> const & trackables, bool & needs_message);
    void _clear_non_marker_trackables(bool & needs_message);
    void _update_document_trackables(document const & d, TUIO2::TuioTime const & session_time, bool & needs_message);
    void _update_stamp_trackables(stamp const & s, TUIO2::TuioTime const & session_time, bool & needs_message);
    void _update_hand_trackables(hand const & h, TUIO2::TuioTime const & session_time, bool & needs_message);
    void _update_touch_trackables(touch const & t, TUIO2::TuioTime const & session_time, bool & needs_message);
    void _remove_untracked_objects(std::vector<std::unique_ptr<Trackable>> const & trackables, bool & needs_message);
    void _collect_ids_of_marker_trackables(int const type_id, std::vector<long> & ids, std::vector<std::unique_ptr<Trackable>> const & trackables);
    void _delete_dead_objects(std::map<int, TUIO2::TuioObject *> & map, bool & needs_message, std::vector<long> const & ids);

    template <typename _T>
    void _update_existing_marker_objects(_T const & o, TrackableTypes type)
    {
        TUIO2::TuioToken *t = type_id_2_objects_map_with_object_id_2_object[type][o.id()]->getTuioToken();

        server->updateTuioToken(t, t->getX(), t->getY(), t->getAngle());
        server->updateTuioBounds(type_id_2_objects_map_with_object_id_2_object[type][o.id()]->getTuioBounds(),
                                 o.center().x, o.center().y,
                                 o.angle(), o.width(), o.height(), 0.0f);
    }

    template <typename _T>
    void _create_new_objects(_T const & o, TUIO2::TuioTime const & session_time, TrackableTypes type)
    {
        TUIO2::TuioObject *object = server->createTuioObject();

        object->setTuioToken(new TUIO2::TuioToken(session_time, nullptr, (unsigned int) type,
                                                  (unsigned int) 1, (unsigned int) o.id(), 0.0f,
                                                  0.0f, 0.0f));

        object->setTuioBounds(new TUIO2::TuioBounds(session_time, nullptr, o.center().x,
                                                    o.center().y, o.angle(), o.width(),
                                                    o.height(), 0.0f));


        type_id_2_objects_map_with_object_id_2_object[type].insert(std::pair<int, TUIO2::TuioObject *>((int) o.id(), object));
    }

    bool _clear_tracked_objects();
};


#endif // MTT_MESSAGING_HANDLER_H
