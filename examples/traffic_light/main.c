#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdlib.h>
#include "smg_traffic_light.h"

int main(int argc, char** argv) {
    smg_traffic_light_state_machine_t sm;
    uint32_t cars, last_cars;

    srand(0);
    smg_traffic_light_init(&sm);
    cars = 0;
    last_cars = 0;


    while (true) {
        if (rand() % 10 == 0) {
            printf("car has arrived\n");
            cars += 1;
        }

        sm.env.car_waiting = (cars > 0);

        smg_traffic_light_step(&sm);

        switch (sm.state) {
            case SMG_TRAFFIC_LIGHT_STATE_GREEN:
            case SMG_TRAFFIC_LIGHT_STATE_YELLOW:
                if (cars > 0) {
                    cars -= 1;
                    printf("car has left, %u remain\n", cars);
                }
                break;
            case SMG_TRAFFIC_LIGHT_STATE_RED:
                if (last_cars != cars) {
                    printf("%u cars are waiting\n", cars);
                }
                break;
            default:
                break;
        }
        last_cars = cars;
        usleep(50000);
    }

    return 0;
}
