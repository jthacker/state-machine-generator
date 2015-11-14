#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdlib.h>
#include "smg_garage.h"

int main(int argc, char** argv) {
    smg_garage_state_machine_t sm;

    srand(0);
    smg_garage_init(&sm);
    sm.env.saved_state = SMG_GARAGE_STATE_CLOSED;

    while (true) {
        if (rand() % 10 == 0) {
            sm.env.button_pressed = true;
            printf("button pressed\n");
        }
        printf("motor_speed: %d  door_position: %d\n",
               sm.env.motor_speed,
               sm.env.door_position);

        smg_garage_step(&sm);
        usleep(50000);
    }

    return 0;
}
