/**
 * Generate a state machine for a vending machine
 *
 * Insert money that is >= to the item price, the state machine
 * will switch to vend, decrement its item_count and return change.
 **/

PREFIX(smg_vending);


DECLARE_ENV {
    // Total number of items in the machine
    uint32_t items;

    // Cost of one item
    uint32_t item_price;

    // Total amount of cash received for all items
    uint32_t money_deposited;

    // Current bill that was inserted
    uint32_t bill_inserted;

    // Total amount of cash inserted by current customer
    uint32_t money_inserted;

    // Change returned
    uint32_t change;
}


TRANSITIONS {
    idle -> deposit :: ENV(bill_inserted) > 0;
    idle -> idle;

    deposit -> vend :: ENV(money_inserted) >= ENV(item_price) &&
                       ENV(items) >= 1;
    deposit -> idle;

    vend -> idle;
}


STATE_FN(deposit) {
    ENV(money_inserted) += ENV(bill_inserted);
    ENV(bill_inserted) = 0;
}


STATE_FN(vend) {
    ENV(change) = ENV(money_inserted) - ENV(item_price);
    ENV(money_deposited) += ENV(item_price);
    ENV(money_inserted) = 0;
    ENV(items) -= 1;
}
