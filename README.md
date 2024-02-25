# Garage Door Controller

This project provides a simple way to control a garage door using a Raspberry Pi Pico and a Relay.

It connects to your WiFi, listens on port 80, and triggers the relay for 0.4 seconds.

## Requirements

- Raspberry Pi Pico
- Relay Module
- MicroPython v1.14

## Installation

1. Flash the MicroPython firmware onto your Raspberry Pi Pico.
2. Connect your relay module to the Pico. Control PIN to PIN 1 (GP0).
3. Clone this repository to your local machine.
4. Fill in the SSID and Password for your WiFi in `secrets.py`
5. Upload the `main.py` and `secrets.py` script to your Pico.

You will need to connect the relay output PINs to your garage door opener switch. This project assumes your opener supports a simple physical button that momentarily connects two wires. Your garage door may have a more advanced keypad. Please consult your garage door opener manual for proper connection methods. Proceed as your own risk.

## Usage

The garage door can be controlled by sending HTTP requests to the Pico.

- To open/close the garage door, send a GET request to `/toggle`.

For troubleshooting or reloading python, stop the server by sending a GET request to `/stop`. 

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)