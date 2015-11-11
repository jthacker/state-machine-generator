/**
 * Generate a state machine for a garage door
 *
 * [[[smg]]]
 * prefix: smg_garage
 *
 * states:
 *  init:
 *      opened: ENV.saved_state == STATE(opened) || ENV.saved_state == STATE(opening)
 *      closed: ENV.saved_state == STATE(closed) || ENV.saved_state == STATE(closing)
 *
 *  closed:
 *      opening: ENV.button_pressed
 *
 *  closing:
 *      opening: ENV.button_pressed
 *      closed: ENV.door_position == 0
 *
 *  opened:
 *      closing: ENV.button_pressed
 *
 *  opening:
 *      closing: ENV.button_pressed
 *      opened: ENV.door_position == 100
 *
 *  run_motor:
 *      closing: ENV.motor_speed > 0
 *      opening: ENV.motor_speed < 0
 *
 * [[[end]]]
 *
 * An event is a specially treated bool value.
 * If an event is set in a state function, then it will be once it has been handled.
 * In the example below, the button_pressed event is used to signal that
 * the user would like to toggle the state of the garage door.
 * This event is signaled externally.
 *
 * The light is on whenever the door is moving.
 *
 * The following keywords are treated specially:
 **/

DECLARE_ENV {
    bool light_on;
    int door_position;
    int motor_speed;
    DECLARE_EVENT(button_pressed);
    DECLARE_STATE(saved_state);
}


STATE_FN(init) {
    // Load a saved state from disk
    load_saved_state(&(m->env.saved_state));
}


STATE_FN(closed) {
    m->env.light_on = false;
    m->env.motor_speed = 0;
    m->env.saved_state = STATE(closed);
}


STATE_FN(closing) {
    m->env.button_pressed.handled = true;
    m->env.light_on = true;
    m->env.motor_speed = -1;
    m->env.saved_state = STATE(closing);
}


STATE_FN(opened) {
    m->env.button_pressed.handled = true;
    m->env.light_on = false;
    m->env.motor_speed = 0;
    m->env.saved_state = STATE(opened);
}


STATE_FN(opening) {
    m->env.button_pressed.handled = true;
    m->env.light_on = true;
    m->env.motor_speed = 1;
    m->env.saved_state = STATE(opening);
}


STATE_FN(run_motor) {
    m->env.door_position += m->env.motor_speed;
}
