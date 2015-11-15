#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdlib.h>
#include "smg_traffic_light.h"

int main(int argc, char** argv) {
    smg_traffic_light_state_machine_t sm;
    uint32_t cars;

    srand(0);
    smg_traffic_light_init(&sm);
    cars = 0;


    while (true) {
        if (rand() % 10 == 0) {
            cars += 1;
        }

        sm.env.car_waiting = (cars > 0);

        smg_traffic_light_step(&sm);

        switch (sm.state) {
            case SMG_TRAFFIC_LIGHT_STATE_GREEN:
            case SMG_TRAFFIC_LIGHT_STATE_YELLOW:
                printf("car has left, %u remain\n", cars);
                if (cars > 0) {
                    cars -= 1;
                }
                break;
            case SMG_TRAFFIC_LIGHT_STATE_RED:
                if (cars > 0) {
                    printf("%u cars are waiting\n", cars);
                }
                break;
            default:
                break;
        }
        usleep(50000);
    }

    return 0;
}
