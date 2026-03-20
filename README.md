# SUT — Shimano UART Tool

SUT (Shimano UART Tool) is a Python tool for monitoring and analyzing Shimano e-bike UART traffic.
It can capture messages from Shimano components (battery, motor, display) and optionally send test data via a named pipe.

## Running the Tool

Activate your Python environment and start the tool:

```bash
./run.sh
```

Example output when starting:
```
Activating venv
Start tool
```

Press Ctrl+C to exit cleanly.

## Sending Data via Pipe

SUT can send raw bytes to the bus using a named pipe. This is useful for testing or simulating messages.

The tool takes care of creating the named pipe, so make sure it is running.

Send a test message to the pipe:

```bash
echo -n '\x42\x00' > /tmp/sut_pipe
```
Expected tool output:
```
S: 00 42 00 91 7A
R: 00 C2 00 5D F6
```
S: — message sent to the bus  
R: — message received from the bus

This acts as a simple sanity check to verify the tool is reading and sending messages correctly.

## Colored Output

|Color   |Meaning                    |
|--------|---------------------------|
|(normal)|Valid message received     |
|Yellow  |Incomplete message detected|
|Red     |CRC error detected         |


Press Ctrl+C to exit.  
The tool will cleanly close the serial port and any open pipes.

## Notes

Requires Python 3.8+  
CRC16 calculation and UART parsing are handled automatically  
Currently only tested on BT_E6000  