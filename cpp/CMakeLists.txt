cmake_minimum_required(VERSION 3.9)
project(MTT)

set(CMAKE_CXX_STANDARD 11)

# TUIO1
#set(PATH_LIB ${CMAKE_CURRENT_SOURCE_DIR}/lib/libTUIO.a)
#set(PATH_INCLUDE_TUIO_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/lib/tuio_headers/TUIO)
#set(PATH_INCLUDE_OSC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/lib/tuio_headers/oscpack)
#include_directories(${PATH_INCLUDE_TUIO_HEADERS} ${PATH_INCLUDE_OSC_HEADERS})

# TUIO2
set(PATH_LIB ${CMAKE_CURRENT_SOURCE_DIR}/lib/libTUIO2.a)
set(PATH_INCLUDE_TUIO_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/lib/tuio2_headers/TUIO2)
set(PATH_INCLUDE_OSC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/lib/tuio2_headers/oscpack)
include_directories(${PATH_INCLUDE_TUIO_HEADERS} ${PATH_INCLUDE_OSC_HEADERS})

find_package(OpenCV REQUIRED)

set(THREADS_PREFER_PTHREAD_FLAG ON) # linux only
find_package(Threads REQUIRED) # linux only

add_executable(MTT main.cpp lib/surface.cpp
        lib/surface.h
        util/util.cpp
        util/util.h
        processing/processing.cpp
        processing/processing.h
        processing/marker/marker_creation.cpp
        processing/marker/marker_creation.h
        processing/marker/predefined_markers.h
        processing/datastructures/document.cpp
        processing/datastructures/document.h
        processing/datastructures/stamp.cpp
        processing/datastructures/stamp.h
        math/smath.cpp
        math/smath.h
        messaging/MessagingHandler.cpp
        messaging/MessagingHandler.h
        processing/tracking/TrackableTypes.h
        processing/tracking/Trackable.cpp
        processing/tracking/Trackable.h processing/datastructures/hand.cpp processing/datastructures/hand.h processing/datastructures/touch.cpp processing/datastructures/touch.h util/stime.h)

include_directories(${OpenCV_INCLUDE_DIRS})
target_link_libraries(MTT ${OpenCV_LIBS} ${PATH_LIB} Threads::Threads usb-1.0)