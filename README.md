# g600prog
Utility to read/write Logitech g600 mouse key maps.
Behaves like cp, ie, give it a source and destination.
Note: MOUSE is a special keyword that specifies the mouse rather than a file.

In most cases, this script requires root (ie, run sudo <this script>).

Mouse configurations are stored in a human readable json format by default.
A json byte format (--bytes) is also available, which is more portable
between versions of this tool.

For example, to copy the current mouse config to a file called mouse_config.json:
$ sudo ./g600prog.py MOUSE mouse_config.json

Copying a custom_config.json file to the mouse:
$ sudo ./g600prog.py custom_config.json MOUSE

Leaving off the second argument causes it to print to stdout.
So, to print your current mouse config:
$ sudo ./g600prog.py MOUSE


Each button on the mouse has 3 pieces bytes data:
1. Usb mouse code byte
2. Bit-wise modifier keys (left/right alt, ctrl, shift, etc)
3. USB keyboard scan code.

If the mouse scan code is set to anything other that 0 (NO_MOUSEBUT),
it will override the second two bytes and they will not be sent.

