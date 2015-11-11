/**
 * Generate a state machine for a traffic light
 *
 * [[[smg
 * prefix: smg_traffic_light
 *
 * machine_members:
 *  bool car_waiting
 *  uint32_t cycles
 *
 * states:
 *  red:
 *      green: [m->car_waiting && m->duration > 3]
 *  yellow:
 *      red: [m->duration > 3]
 *  green:
 *      yellow: [m->duration > 10]
 * ]]]
 **/

/**
 * Everytime the red state is entered, count that as one cycle
 **/
state_red {
    m->cycles += 1;
}
