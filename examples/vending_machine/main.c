#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdlib.h>
#include "smg_vending.h"

int main(int argc, char** argv) {
    smg_vending_state_machine_t sm;

    srand(0);
    smg_vending_init(&sm);
    sm.env.items = 10;
    sm.env.item_price = 4;


    while (true) {
        if (rand() % 10 == 0) {
            sm.env.bill_inserted = 1;
            printf("Inserting $%d bill\n", sm.env.bill_inserted);
        }

        smg_vending_step(&sm);

        switch (sm.state) {
            case SMG_VENDING_STATE_VEND:
                printf("Vending item. %d items left\n", sm.env.items);
                break;
            case SMG_VENDING_STATE_DEPOSIT:
                printf("$%d have been inserted\n", sm.env.money_inserted);
                break;
            default:
                break;
        }

        if (sm.env.items == 0) {
            printf("No items left, shutting down\n");
            break;
        }
        usleep(50000);
    }

    return 0;
}
