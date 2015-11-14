/**
 * Generate a state machine for a traffic light.
 *
 * This example demonstrates the use of the system provided duration
 * member. Duration is updated everytime a state transitions to itself and
 * is reset to 0 when it transitions to a new state.
 **/

PREFIX(smg_traffic_light);


DECLARE_ENV {
    /**
     * car_waiting is true anytime a car is at the traffic light
     **/
    bool car_waiting;

    /**
     * count the total number of times the light has fully cycled
     **/
    int cycles;
}


TRANSITIONS {
    red -> green :: ENV(car_waiting) && m->duration > 3;
    red -> red;

    yellow -> red :: m->duration > 3;
    yellow -> yellow;

    green -> yellow :: m->duration > 10;
    green -> green;
}


/**
 * Everytime the red state is entered, count that as one cycle
 **/
STATE_FN(red) {
    ENV(cycles) += 1;
}
