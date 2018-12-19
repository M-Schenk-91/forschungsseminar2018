#include <thread>
#include "MessagingHandler.h"
#include "../math/smath.h"
#include "../processing/tracking/TrackableTypes.h"
#include "../processing/datastructures/hand.h"
#include "../processing/datastructures/touch.h"

MessagingHandler::MessagingHandler()
{
    udp_sender = new TUIO2::UdpSender("127.0.0.1", 3333);
    server = new TUIO2::TuioServer(udp_sender);

    server->sendFullTuioBundle();
    server->disablePeriodicMessages();
    server->setSourceName("TRACKING_BACKEND");
    server->enableFullUpdate();

    type_id_2_objects_map_with_object_id_2_object.insert(
            std::pair<int, std::map<int, TUIO2::TuioObject *>>(TrackableTypes::PHYSICAL_DOCUMENT,
                                                               std::map<int, TUIO2::TuioObject *>()));
    type_id_2_objects_map_with_object_id_2_object.insert(
            std::pair<int, std::map<int, TUIO2::TuioObject *>>(TrackableTypes::TANGIBLE,
                                                               std::map<int, TUIO2::TuioObject *>()));
    type_id_2_objects_map_with_object_id_2_object.insert(
            std::pair<int, std::map<int, TUIO2::TuioObject *>>(TrackableTypes::HAND,
                                                               std::map<int, TUIO2::TuioObject *>()));
    type_id_2_objects_map_with_object_id_2_object.insert(
            std::pair<int, std::map<int, TUIO2::TuioObject *>>(TrackableTypes::TOUCH,
                                                               std::map<int, TUIO2::TuioObject *>()));
}

MessagingHandler::~MessagingHandler()
{
    this->_clear_tracked_objects();

    delete server;

    udp_sender = nullptr;
    server = nullptr;
}

void MessagingHandler::send_message(std::vector<std::unique_ptr<Trackable>> const & trackables, bool threaded)
{
    bool needs_message = false;

    if(trackables.empty())
        needs_message = _clear_tracked_objects();
    else
        _update_tracked_objects(trackables, needs_message);

    if(needs_message)
    {
        server->commitTuioFrame();
    }
}

void MessagingHandler::_clear_non_marker_trackables(bool & needs_message)
{
    std::vector<TUIO2::TuioObject *> to_delete;

    for(auto & item : server->getTuioObjectList())
        if(item->getTuioToken()->getTypeID() == TrackableTypes::TOUCH)
            to_delete.push_back(item);

    if(!to_delete.empty())
    {
        type_id_2_objects_map_with_object_id_2_object[TrackableTypes::TOUCH].clear();

        for(auto & item : to_delete)
            server->removeTuioObject(item);

        needs_message = true;
    }
}

void MessagingHandler::_update_document_trackables(document const & d, TUIO2::TuioTime const & session_time, bool & needs_message)
{
    needs_message = true;

    if (type_id_2_objects_map_with_object_id_2_object[TrackableTypes::PHYSICAL_DOCUMENT].count(d.id()))
        _update_existing_marker_objects(d, TrackableTypes::PHYSICAL_DOCUMENT);
    else
        _create_new_objects(d, session_time, TrackableTypes::PHYSICAL_DOCUMENT);
}

void MessagingHandler::_update_stamp_trackables(stamp const & s, TUIO2::TuioTime const & session_time, bool & needs_message)
{
    needs_message = true;

    if (type_id_2_objects_map_with_object_id_2_object[TrackableTypes::TANGIBLE].count(s.id()))
        _update_existing_marker_objects(s, TrackableTypes::TANGIBLE);
    else
        _create_new_objects(s, session_time, TrackableTypes::TANGIBLE);
}

void MessagingHandler::_update_hand_trackables(hand const & h, TUIO2::TuioTime const & session_time, bool & needs_message)
{
    needs_message = true;

    if (type_id_2_objects_map_with_object_id_2_object[TrackableTypes::HAND].count(h.id()))
        _update_existing_marker_objects(h, TrackableTypes::HAND);
    else
        _create_new_objects(h, session_time, TrackableTypes::HAND);
}

void MessagingHandler::_update_touch_trackables(touch const & t, TUIO2::TuioTime const & session_time, bool & needs_message)
{
    needs_message = true;

    _create_new_objects(t, session_time, TrackableTypes::TOUCH);
}

void MessagingHandler::_update_tracked_objects(std::vector<std::unique_ptr<Trackable>> const & trackables, bool & needs_message)
{
    _clear_non_marker_trackables(needs_message);

    TUIO2::TuioTime session_time = TUIO2::TuioTime::getSystemTime();
    server->initTuioFrame(session_time);

    for (auto const & trackable : trackables)
    {
        switch (trackable->type_id())
        {
            case TrackableTypes::PHYSICAL_DOCUMENT:
                _update_document_trackables(*(document *) trackable.get(), session_time, needs_message);
            break;

            case TrackableTypes::TANGIBLE:
                _update_stamp_trackables(*(stamp *) trackable.get(), session_time, needs_message);
            break;
            case TrackableTypes::HAND:
                _update_hand_trackables(*(hand *) trackable.get(), session_time, needs_message);
            break;
            case TrackableTypes::TOUCH:
                _update_touch_trackables(*(touch *) trackable.get(), session_time, needs_message);
            break;
        }
    }

    _remove_untracked_objects(trackables, needs_message);
}

void MessagingHandler::_remove_untracked_objects(std::vector<std::unique_ptr<Trackable>> const & trackables, bool & needs_message)
{
    for (auto i = type_id_2_objects_map_with_object_id_2_object.begin(); i != type_id_2_objects_map_with_object_id_2_object.end(); ++i)
    {
        std::vector<long> ids;

        _collect_ids_of_marker_trackables(i->first, ids, trackables);

        switch(i->first)
        {
            case TrackableTypes::PHYSICAL_DOCUMENT:
            case TrackableTypes::TANGIBLE:
            case TrackableTypes::HAND:
                _delete_dead_objects(i->second, needs_message, ids);
            break;
            default:
                return;
        }
    }
}

void MessagingHandler::_collect_ids_of_marker_trackables(int const type_id, std::vector<long> & ids, std::vector<std::unique_ptr<Trackable>> const & trackables)
{
    for(auto & t : trackables)
    {
        if (t->type_id() == type_id)
        {
            switch(type_id)
            {
                case TrackableTypes::PHYSICAL_DOCUMENT:
                    ids.push_back(((document *) t.get())->id());
                    break;
                case TrackableTypes::TANGIBLE:
                    ids.push_back(((stamp *) t.get())->id());
                    break;
                case TrackableTypes::HAND:
                    ids.push_back(((hand *) t.get())->id());
                    break;
                default:
                    return;
            }
        }
    }
}

void MessagingHandler::_delete_dead_objects(std::map<int, TUIO2::TuioObject *> & map, bool & needs_message, std::vector<long> const & ids)
{
    std::vector<long> ids_to_delete;

    for(auto k = map.begin(); k != map.end(); ++k)
    {
        if(std::find(ids.begin(), ids.end(), k->first) == ids.end())
        {
            needs_message = true;

            ids_to_delete.push_back(k->first);
        }
    }

    for(auto const & id : ids_to_delete)
    {
        server->removeTuioObject(map[id]);
        map.erase(id);
    }
}

bool MessagingHandler::_clear_tracked_objects()
{
    bool needs_message = false;

    for (auto i = type_id_2_objects_map_with_object_id_2_object.begin(); i != type_id_2_objects_map_with_object_id_2_object.end(); ++i)
    {
        if(!i->second.empty())
        {
            i->second.clear();

            needs_message = true;
        }
    }

    if(needs_message)
        server->resetTuioObjectList();

    return needs_message;
}