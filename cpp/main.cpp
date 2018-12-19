#include "processing/processing.h"
#include "util/util.h"

int main(int argc, char ** argv)
{
    proc::initialize();
    proc::update();
    proc::destroy();

    return 0;
}