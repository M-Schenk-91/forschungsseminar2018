#ifndef UNTITLED1_PROCESSING_H
#define UNTITLED1_PROCESSING_H

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>
#include "../lib/surface.h"
#include "datastructures/document.h"
#include "../messaging/MessagingHandler.h"
#include "datastructures/hand.h"
#include "datastructures/touch.h"
#include "../math/smath.h"

#define SIZE 4

namespace proc
{
    const int DEFAULT_SCREEN_SETTINGS = 0x6C; // 0x8C V 0x68

    enum screen_mode
    {
        FULLSCREEN,
        ORIGINAL
    };

    void initialize();
    void update();
    void retrieve_raw_image(cv::Mat & frame);
    void track_markers(cv::Mat const & frame);

    template <typename _T>
    void handle_marker_based_tracking(std::vector<std::unique_ptr<Trackable>> & trackables,
                                      std::vector<std::vector<cv::Point2f>> const & corners,
                                      std::vector<_T> & objects, std::vector<uint8_t> const & ids)
    {
        for (uint32_t i = 0; i < corners.size(); i++)
        {
            for (auto o = objects.begin(); o != objects.end(); ++o)
            {
                if (o->id() == ids[i])
                {

                    std::unique_ptr<Trackable> d(new _T(o->id(), o->marker_bits(), o->marker_size(),
                                                        o->name(), o->type()));
                    d->set_roi(corners[i], SIZE);

                    trackables.push_back(std::move(d));
                }
            }
        }
    }

    void handle_processing_timing(double & last_time, double & unprocessed_time, double & frame_counter, int & frames, int & last_fps, bool & tracking);
    void perform_tracking_step(std::vector<std::unique_ptr<Trackable>> & trackables, cv::Mat & frame, MessagingHandler & msg_handler, int const last_fps);
    void handle_hand_tracking(std::vector<std::unique_ptr<Trackable>> & trackables, cv::Mat & frame, cv::Scalar const & lower_bound = cv::Scalar(0, 0, 0),
                              cv::Scalar const & upper_bound = cv::Scalar(0, 0, 0), bool to_threshold = false);
    void handle_touch_tracking(std::vector<std::unique_ptr<Trackable>> & trackables, cv::Mat & frame);
    void threshold(cv::Mat & frame, const cv::Scalar &lower_bound, const cv::Scalar &upper_bound);
    void find_relevant_contours(std::vector<std::vector<cv::Point>> & contours, cv::Mat const & frame, float area_sentinel);
    //void detect_stamping();
    void draw(cv::Mat & frame, std::vector<std::unique_ptr<Trackable>> const & trackables, int const frames);
    void calibrate(int mode = DEFAULT_SCREEN_SETTINGS);
    void display(cv::Mat & _image, char const * _name, screen_mode const _mode);
    void convex_hull(std::vector<int> & hull, std::vector<cv::Point> & hull_points, std::vector<cv::Point> & contour);
    void detect_hands(std::vector<std::unique_ptr<Trackable>> & trackables, std::vector<std::vector<cv::Point>> & contours);
    void retrieve_touches(std::vector<std::unique_ptr<Trackable>> & touches, int size_factor=1);
    void filter_false_positive_touches(std::vector<std::unique_ptr<Trackable>> & trackables, std::vector<std::unique_ptr<Trackable>> & source);
    void retrieve_roi_from_touch_blob(std::vector<cv::Point2f> & roi, surface_blob const & blob, int size_factor);
    void create_touch_trackable(std::unique_ptr<Trackable> & t, surface_blob const & blob, int size_factor);
    void evaluate_hand_contour_candidate(std::vector<std::unique_ptr<Trackable>> & trackables, std::vector<cv::Point> & contour, int & id);
    void create_hand_trackable(std::vector<std::unique_ptr<Trackable>> & trackables, int & id, cv::Point & hand_center,std::vector<cv::Point> & finger_tips, std::vector<cv::Point> const & complete_hull);
    void evaluate_defect(cv::Point & hand_center, std::vector<cv::Point> & finger_tips, int & count, cv::Vec4i const & defect, std::vector<cv::Point> const & contour);

    int sufficient_hand_defect_angles(cv::Point & hand_center, std::vector<cv::Point> & finger_tips, std::vector<cv::Point> const & contour, std::vector<cv::Vec4i> const & defects, float const lower_angle_bound, float const upper_angle_bound);

    bool destroy();
}

#endif //UNTITLED1_PROCESSING_H
