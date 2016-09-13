# smg: State Machine Generator

## Install
```
$ pip install https://github.com/jthacker/state-machine-generator
```

## Usage
First, create a config, see `examples/traffic_light/config.h`
```c
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
    red -> green :: ENV(car_waiting) && m->duration > 30;
    red -> red;

    yellow -> red :: m->duration > 5;
    yellow -> yellow;

    green -> yellow :: m->duration > 30;
    green -> green;
}


/**
 * Everytime the red state is entered, count that as one cycle
 **/
STATE_FN(red) {
    ENV(cycles) += 1;
}
```

Run the generator
```bash
> smg config.h ./
```

Creates `smg_traffic_light.c` and `smg_traffic_light.h`
