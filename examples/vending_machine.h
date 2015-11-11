/**
 * Generate a state machine for a vending machine
 *
 * [[[smg
 * prefix: smg_vending
 *
 * machine_members:
 *  uint item_price
 *  uint money_deposited
 *  uint money_inserted
 *  uint change
 *
 * states:
 *  idle:
 *      deposit: [m->money_inserted]
 *      idle
 *  deposit:
 *      vend: [m->money_desposited >= m->item_price]
 *      idle
 *  vend:
 *      idle
 * ]]]
 **/

state_deposit {
    m->money_deposited += m->money_inserted;
    m->money_inserted = 0;
}

state_vend {
    m->change = m->money_deposited - m->item_price;
    m->money_deposited = 0;
}
