/**
 * Garage Door state machine
 **/

/**
 * Setting a prefix allows the generated state machine to
 * be properly namespaced
 **/
PREFIX(smg_garage);


/**
 * ENV is used to define members in the environment struct
 * of the state machine.
 **/
DECLARE_ENV {
    /**
     * Declare button_pressed as an event
     **/
    DECLARE_EVENT(button_pressed);

    /**
     * Declare a member in ENV named saved_state
     * The type is defined as the local enum containing
     * all the states of the state machine
     **/
    DECLARE_STATE(saved_state);

    /**
     * Light should be turned on whenever the motor is running
     **/
    bool light_on;

    /**
     * Position of door from 0 to 100
     * 0 is closed
     * 100 is fully open
     **/
    int door_position;

    /**
     * Motor speed
     * values < 0 will decrease the door_position
     * values > 0 will increase the door_position
     **/
    int motor_speed;
}


/**
 * Describe each transition that a state can make.
 *
 * Syntax:
 * <from_state> -> <to_state> :: <guards>;
 *
 * A transition will take place if the guards block evaluates to
 * true. Transitions are evaluated in order so the first one that
 * is true will be the state returned.
 *
 * If none of the guards evaluate to true, then the error state is
 * entered (default action is to halt).
 * To avoid this, a state that wishes to remain active should transition
 * back to itself with no guards
 **/
TRANSITIONS {
    init -> opened :: ENV(saved_state) == STATE(opened);
    init -> opened :: ENV(saved_state) == STATE(opening);

    init -> closed :: ENV(saved_state) == STATE(closed);
    init -> closed :: ENV(saved_state) == STATE(closing);

    closed -> opening :: ACCEPT(button_pressed);
    // No guards indicates this is a default transition
    closed -> closed;

    closing -> opening :: ACCEPT(button_pressed);
    closing -> closed  :: ENV(door_position) == 0;
    closing -> run_motor;

    opened -> closing :: ACCEPT(button_pressed);
    opened -> opened;

    opening -> closing :: ACCEPT(button_pressed);
    opening -> opened  :: ENV(door_position) == 100;
    opening -> run_motor;

    run_motor -> closing :: ENV(motor_speed) > 0;
    run_motor -> opening :: ENV(motor_speed) < 0;
}


STATE_FN(init) {
    // Pretend function that loads a saved state from disk
    load_saved_state(&(ENV(saved_state)));
}


STATE_FN(closed) {
    ENV(light_on) = false;
    ENV(motor_speed) = 0;
    ENV(saved_state) = STATE(closed);
}


STATE_FN(closing) {
    ENV(light_on) = true;
    ENV(motor_speed) = -1;
    ENV(saved_state) = STATE(closing);
}


STATE_FN(opened) {
    ENV(light_on) = false;
    ENV(motor_speed) = 0;
    ENV(saved_state) = STATE(opened);
}


STATE_FN(opening) {
    ENV(light_on) = true;
    ENV(motor_speed) = 1;
    ENV(saved_state) = STATE(opening);
}


STATE_FN(run_motor) {
    ENV(door_position) += ENV(motor_speed);
}
