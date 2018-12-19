#include <zconf.h>
#include "processing.h"
#include "marker/predefined_markers.h"
#include "marker/marker_creation.h"
#include "../util/util.h"
#include "../math/smath.h"
#include "../messaging/MessagingHandler.h"
#include "tracking/Trackable.h"
#include "datastructures/touch.h"
#include "../util/stime.h"

#define DEBUG 1

libusb_device_handle * s40;
std::vector<document> documents;
std::vector<stamp> stamps;
std::vector<hand> hands;
cv::Ptr<cv::aruco::Dictionary> documents_dictionary;
cv::Ptr<cv::aruco::Dictionary> stamp_dictionary;
std::vector<std::vector<cv::Point2f>> corners_documents, corners_stamps;
std::vector<uint8_t> ids_documents, ids_stamps, ids_hands;

int concurrent_hand_id = 0;

double const DESIRED_FPS = 60.0;
double const FRAME_TIME = 1.0 / DESIRED_FPS;

void proc::initialize()
{
    usleep(1000000);
    s40 = sur40_get_device_handle();

    calibrate(DEFAULT_SCREEN_SETTINGS);

    documents = std::vector<document>
    {
        document(0, proc::mkr::predefined_markers_6x6[0], 6, "document_1"),
        document(1, proc::mkr::predefined_markers_6x6[1], 6, "document_2")
    };

    stamps = std::vector<stamp>
    {
        stamp(0, proc::mkr::predefined_markers_4x4[0], 4, "stamp_1", stamp::stamp_type::ACCEPT),
        stamp(1, proc::mkr::predefined_markers_4x4[1], 4, "stamp_2", stamp::stamp_type::REJECT),
        stamp(2, proc::mkr::predefined_markers_4x4[2], 4, "stamp_3", stamp::stamp_type::NOTED),
        stamp(3, proc::mkr::predefined_markers_4x4[3], 4, "stamp_4", stamp::stamp_type::ACCEPT)
    };

    documents_dictionary = proc::mkr::marker_dictionary_from_physical_object_list(documents);
    stamp_dictionary = proc::mkr::marker_dictionary_from_physical_object_list(stamps);
}

void proc::update()
{
    double last_time = Time::time();
    double unprocessed_time = 0.0;
    double frame_counter = 0.0;

    int frames = 0;
    int last_fps = 0;

    std::vector<std::unique_ptr<Trackable>> trackables;
    MessagingHandler msg_handler;
    cv::Mat frame;

    for (;;)
    {
        bool tracking = false;

        handle_processing_timing(last_time, unprocessed_time, frame_counter, frames, last_fps, tracking);

        if(tracking)
        {
            frames++;
            perform_tracking_step(trackables, frame, msg_handler, last_fps);
        }

        if ((cv::waitKey(1) & 0xFF) == 27)
            break;
    }
}

void proc::handle_processing_timing(double & last_time, double & unprocessed_time, double & frame_counter, int & frames, int & last_fps, bool & tracking)
{
    double start_time = Time::time();
    double passed_time = start_time - last_time;
    last_time = start_time;

    unprocessed_time += passed_time;
    frame_counter += passed_time;

    if(frame_counter > 1.0)
    {
        last_fps = frames;

        frame_counter = 0.0;
        frames = 0;
    }

    for(Time::set_time_delta(FRAME_TIME); unprocessed_time > FRAME_TIME; unprocessed_time -= FRAME_TIME, tracking = true);
}

void proc::perform_tracking_step(std::vector<std::unique_ptr<Trackable>> & trackables, cv::Mat & frame, MessagingHandler & msg_handler, int const last_fps)
{
    retrieve_raw_image(frame);
    track_markers(frame);
    handle_marker_based_tracking(trackables, corners_documents, documents, ids_documents);
    handle_marker_based_tracking(trackables, corners_stamps, stamps, ids_stamps);
    //handle_hand_tracking(trackables, frame, cv::Scalar(25, 25, 25), cv::Scalar(85, 85, 85), false);
    handle_touch_tracking(trackables, frame);

    msg_handler.send_message(trackables);

    if(DEBUG)
    {
        cv::cvtColor(frame, frame, cv::COLOR_GRAY2BGR);
        draw(frame, trackables, last_fps);
    }

    trackables.clear();
}

bool proc::destroy()
{
    sur40_close_device(s40);
}

/*
detect_stamping();

for(auto d = documents.begin(); d != documents.end(); ++d)
{
    util::print("Document: " + std::to_string(d->id()) + " is stamped with: ");

    const auto & stamp_signatures = d->get_stamp_signatures();

    for(auto sts = stamp_signatures.begin(); sts != stamp_signatures.end(); ++sts)
    {
        util::print(* sts);
    }

    util::print("-----------------------------");
}
*/

void proc::handle_hand_tracking(std::vector<std::unique_ptr<Trackable>> & trackables, cv::Mat & frame, const cv::Scalar &lower_bound,
                                const cv::Scalar &upper_bound, bool to_threshold)
{
    std::vector<std::vector<cv::Point>> contours;

    if(to_threshold)
        threshold(frame, lower_bound, upper_bound);

    find_relevant_contours(contours, frame, 4500.0f);
    detect_hands(trackables, contours);
}

void proc::handle_touch_tracking(std::vector<std::unique_ptr<Trackable>> & trackables, cv::Mat & frame)
{
    std::vector<std::unique_ptr<Trackable>> touches;

    retrieve_touches(touches, SIZE);
    filter_false_positive_touches(trackables, touches);
}

void proc::filter_false_positive_touches(std::vector<std::unique_ptr<Trackable>> & trackables, std::vector<std::unique_ptr<Trackable>> & source)
{
    std::vector<int> temp;

    for(int i = 0; i < source.size(); i++)
    {
        bool is_part = false;

        for (auto & trackable : trackables)
        {
            if (trackable->type_id() == TrackableTypes::HAND)
            {
                std::vector<cv::Point2f> hull;

                auto const & rr = cv::minAreaRect(((hand *) trackable.get())->complete_hull());

                cv::Point2f points[4];
                rr.points(points);

                for (int k = 0; k < 4; k++)
                    hull.push_back(points[k]);

                if ((is_part = math::is_point_in_convex_polygon(source[i]->center(), hull) || math::is_point_in_convex_polygon(source[i]->center(), trackable->roi())))
                    break;
            }
            else
            {
                if ((is_part = math::is_point_in_convex_polygon(source[i]->center(), trackable->roi())))
                    break;
            }
        }

        if (!is_part)
            temp.push_back(i);
    }

    for(auto & i : temp)
        trackables.push_back(std::move(* (source.begin() + i)));
}

void proc::retrieve_touches(std::vector<std::unique_ptr<Trackable>> & touches, int size_factor)
{
    surface_blob blobs[128];

    int num_blobs = surface_get_blobs(s40, blobs);

    for (int i = 0; i < num_blobs; i++)
    {
        if (blobs[i].type == 0x02)
        {
            std::unique_ptr<Trackable> t;

            create_touch_trackable(t, blobs[i], size_factor);

            touches.push_back(std::move(t));
        }
    }
}

void proc::retrieve_roi_from_touch_blob(std::vector<cv::Point2f> & roi, surface_blob const & blob, int size_factor)
{
    roi = std::vector<cv::Point2f>
    {
            cv::Point2f(blob.bb_pos_x, blob.bb_pos_y), // tlc
            cv::Point2f(blob.bb_pos_x, blob.bb_pos_y + blob.bb_size_y), // blc
            cv::Point2f(blob.bb_pos_x + blob.bb_size_x, blob.bb_pos_y + blob.bb_size_y), // brc
            cv::Point2f(blob.bb_pos_x + blob.bb_size_x, blob.bb_pos_y) // trc
    };
}

void proc::create_touch_trackable(std::unique_ptr<Trackable> & t, surface_blob const & blob, int size_factor)
{
    std::vector<cv::Point2f> roi;

    retrieve_roi_from_touch_blob(roi, blob, size_factor);

    t = std::unique_ptr<Trackable>(new touch(blob.blob_id, cv::Point2f(blob.pos_x, blob.pos_y)  / size_factor,blob.area));

    t->set_center(cv::Point2f(blob.ctr_x, blob.ctr_y));
    t->set_angle(math::to_degrees(blob.angle));
    t->set_width(blob.bb_size_x);
    t->set_height(blob.bb_size_y);
    t->set_roi(roi, SIZE);
}

void proc::detect_hands(std::vector<std::unique_ptr<Trackable>> & trackables, std::vector<std::vector<cv::Point>> & contours)
{
    int id = 0;

    for (auto &contour : contours)
        evaluate_hand_contour_candidate(trackables, contour, id);

    std::vector<int> th_ids;

    bool has_hand = false;

    for (auto const &t : trackables) {
        if (t->type_id() == TrackableTypes::HAND) {
            has_hand = true;
            th_ids.push_back(((hand *) t.get())->id());
        }
    }

    if (has_hand) {
        for (auto it = hands.begin(); it != hands.end();) {
            bool has_hit = false;

            for (auto id : th_ids) {
                if (it->id() == id)
                    has_hit = true;
            }

            if (!has_hit)
                it = hands.erase(it);
            else
                ++it;
        }
    } else
        hands.clear();
}

void proc::evaluate_hand_contour_candidate(std::vector<std::unique_ptr<Trackable>> & trackables, std::vector<cv::Point> & contour, int & id)
{
    std::vector<cv::Vec4i> defects;
    std::vector<int> hull;
    std::vector<cv::Point> hull_points, finger_tips;
    cv::Point hand_center;

    convex_hull(hull, hull_points, contour);

    cv::convexityDefects(contour, hull, defects);

    if(sufficient_hand_defect_angles(hand_center, finger_tips, contour, defects, 20.0f, 65.0f) > 2)
        create_hand_trackable(trackables, id, hand_center, finger_tips, hull_points);
}

void proc::create_hand_trackable(std::vector<std::unique_ptr<Trackable>> & trackables, int & id, cv::Point & hand_center,std::vector<cv::Point> & finger_tips, std::vector<cv::Point> const & complete_hull)
{
    std::vector<cv::Point2f> hand_rect_points;

    cv::Rect aabb = cv::boundingRect(finger_tips);

    cv::Point2f hc(hand_center.x, hand_center.y);

    math::approximate_hand_roi<cv::Point2f>(hand_rect_points, aabb, hc, 12000);

    std::unique_ptr<Trackable> h(new hand(concurrent_hand_id++, hand_center, finger_tips, complete_hull));
    h->set_roi(hand_rect_points, SIZE);

    bool is_new = true;

    for(int i = 0; i < hands.size(); i++)
    {
        if(std::abs(hands[i].center().x - h->center().x) < 10 && std::abs(hands[i].center().y - h->center().y) < 10 && std::abs(hands[i].angle() - h->angle()) < 5)
        {
            is_new = false;
            ((hand *) h.get())->set_id(hands[i].id());
            hands[i] = * ((hand *) h.get());
            break;
        }
    }

    if(h->roi().size() == 4)
    {
        if(is_new)
            hands.push_back( * ((hand *) h.get()));

        trackables.push_back(std::move(h));
    }
}

int proc::sufficient_hand_defect_angles(cv::Point & hand_center, std::vector<cv::Point> & finger_tips, std::vector<cv::Point> const & contour, std::vector<cv::Vec4i> const & defects, float const lower_angle_bound, float const upper_angle_bound)
{
    int count = 0;

    if(defects.size() > 3)
    {
        for(int i = 0; i < defects.size(); i++)
            evaluate_defect(hand_center, finger_tips, count, defects[i], contour);

        hand_center = count ? hand_center / count : cv::Point(-1, -1);
    }

    return count;
}

void proc::evaluate_defect(cv::Point & hand_center, std::vector<cv::Point> & finger_tips, int & count, cv::Vec4i const & defect, std::vector<cv::Point> const & contour)
{
    if (defect[3] > 13 * 256)
    {
        float angle = math::angle_degrees(contour[defect[2]] - contour[defect[0]], contour[defect[2]] - contour[defect[1]]);

        if (angle > 19 && angle < 71)
        {
            finger_tips.push_back(contour[defect[0]]);
            finger_tips.push_back(contour[defect[1]]);

            ++count;

            hand_center += contour[defect[2]];
        }
    }
}

void proc::convex_hull(std::vector<int> & hull, std::vector<cv::Point> & hull_points,
                       std::vector<cv::Point> & contour)
{
    cv::convexHull(contour, hull);

    for (auto const & i : hull)
        hull_points.push_back(contour[i]);
}

void proc::threshold(cv::Mat &frame, const cv::Scalar & lower_bound, const cv::Scalar & upper_bound)
{
    cv::inRange(frame, lower_bound, upper_bound, frame);
    cv::medianBlur(frame, frame, 7);
}

void proc::find_relevant_contours(std::vector<std::vector<cv::Point>> & contours, cv::Mat const & frame, float area_sentinel)
{
    std::vector<cv::Vec4i> hierarchy;
    std::vector<std::vector<cv::Point>> all_contours;

    cv::findContours(frame, all_contours, hierarchy, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE, cv::Point(0, 0));

    if(!all_contours.empty())
    {
        for(auto const & c : all_contours)
            if (cv::contourArea(c) > area_sentinel)
                contours.push_back(c);
    }
}

void proc::retrieve_raw_image(cv::Mat & frame)
{
    uint8_t raw[VIDEO_BUFFER_SIZE];

    surface_get_image(s40, raw);

    frame = cv::Mat(cv::Size(VIDEO_RES_X, VIDEO_RES_Y), CV_8UC1, raw).clone();

    cv::resize(frame, frame, cv::Size(1920 / 4, 1080 / 4));
}

void proc::track_markers(cv::Mat const & frame)
{
    cv::aruco::detectMarkers(frame, documents_dictionary, corners_documents, ids_documents);
    cv::aruco::detectMarkers(frame, stamp_dictionary, corners_stamps, ids_stamps);
}

/*
void proc::detect_stamping()
{
    if (ids_documents.size() == 0)
        return;

    for(document & pd : documents)
    {
        for(uint8_t did : ids_documents)
        {
            if(pd.id() == did)
            {
                for(stamp & ps : stamps)
                {
                    bool is_in_convex_polygon = false;

                    for(const cv::Point2f & p : ps.roi())
                    {
                        is_in_convex_polygon = math::is_point_in_convex_polygon(p, pd.roi());

                        if(!is_in_convex_polygon)
                            break;
                    }

                    if(is_in_convex_polygon)
                        pd.add_stamp_signature(ps);
                }

                break;
            }
        }
    }
}
*/
void proc::draw(cv::Mat & frame, std::vector<std::unique_ptr<Trackable>> const & trackables, int const frames)
{
    for(auto & t : trackables)
        t->draw(frame, SIZE);

    cv::putText(frame, "FPS: " + std::to_string(frames), cv::Point(15, 15), 1.2, 1.2, cv::Scalar(0, 0, 255));

    display(frame, "TEST", screen_mode::ORIGINAL);
}

void proc::calibrate(int mode)
{
    switch (mode)
    {
        case DEFAULT_SCREEN_SETTINGS: surface_set_vsvideo(s40, DEFAULT_SCREEN_SETTINGS); break;
        default: return;
    }
}

void proc::display(cv::Mat & _image, char const * _name, screen_mode const _mode)
{
    switch(_mode)
    {
        case screen_mode::FULLSCREEN:
        {
            cv::namedWindow(_name, CV_WINDOW_NORMAL);
            cv::setWindowProperty(_name, CV_WND_PROP_FULLSCREEN, cv::WINDOW_FULLSCREEN);
            cv::imshow(_name, _image);
        }
        break;

        case screen_mode::ORIGINAL:
        {
            cv::imshow(_name, _image);
        }
        break;
    }
}