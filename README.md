# g600prog
## Overview
Utility to read/write Logitech g600 mouse key maps.
Behaves like cp, ie, give it a source and destination.
Note: MOUSE is a special keyword that specifies the mouse rather than a file.

In most cases, this script requires root (ie, run sudo <this script>).
Why? Two reasons: 
- To gain access to the usb configuration interface
- To temporarily detach other drivers from the mouse when doing updates

Mouse configurations are stored in a human readable json format by default.
A json byte format (`--bytes`) is also available, which is a portable
between versions of this tool.

For example, to copy the current mouse configuration to a file called mouse_config.json:
```
$ sudo ./g600prog.py MOUSE mouse_config.json
```

Copying a custom_config.json file to the mouse:
```
$ sudo ./g600prog.py custom_config.json MOUSE
```

Leaving off the second argument causes it to print to stdout.
So, to print your current mouse config:
```
$ sudo ./g600prog.py MOUSE
```

## Modes and gshift
The g600 has 3 modes of configuration.
Each of these is a totally independent mapping, DPI, and lighting settings.
Mode 1 is the default mode.
The Mouse button code: `MODE_SWITCH` will cycle the mouse to the next mode.

Each mode actually has two button mappings, Normal and G-shifted.
While holding down the mouse button with the `GSHIFT` code bound, the mouse will take on the buttonMapShifted
 

## Byte to name translator.
In `--bytes` mode, there three arrays of the raw bytes, one for each mode.
In the default human readable mode, the bytes are translated to understandable names.
These names are discussed in the following sections.
Note, if a byte does not map in any of the namings, it will appear as `UNDEFINEDXXX` where `XXX` is a 3-digit decimal representation of the byte.

## DPI / Poll Rate
DPI bytes are effectively multiplied by 50 to be the human readable (and actual) DPI number.
Max DPI for this mouse is 8200.

Poll rate bytes are translated to the human readable (and actual) polling rate by the following formula:
ActualPollrate = int(1000 / (1 + int(byte)))
Max pollrate is 1000

## Buttons
Each button on the mouse has 3 pieces bytes data:
- USB mouse code byte
- Bit-wise modifier keys (left/right alt, ctrl, shift, etc)
- USB keyboard scan code.

If the mouse scan code is set to anything other that 0 (NO_MOUSEBUT),
it will override the second two bytes and they will not be used.


### Mouse Button Codes
```
| Byte | Name         |
|------+--------------|
| 0x00 | NO_MOUSEBUT  |
| 0x01 | LEFT_CLICK   |
| 0x02 | RIGHT_CLICK  |
| 0x03 | MIDDLE_CLICK |
| 0x04 | BACK         |
| 0x05 | FORWARD      |
| 0x06 | MOUSE6       |
| 0x07 | MOUSE7       |
| 0x11 | DPI_UP       |
| 0x12 | DPI_DOWN     |
| 0x13 | DPI_CYCLING  |
| 0x14 | MODE_SWITCH  |
| 0x15 | DPI_SHIFT    |
| 0x16 | DPI_DEFAULT  |
| 0x17 | GSHIFT       |
```

### Keyboard Modifier Codes (left-alt, right-shift, etc)
```
| Bit set | Name   |
|---------+--------|
|       0 | LCTRL  |
|       1 | LSHIFT |
|       2 | LALT   |
|       3 | LGUI   |
|       4 | RCTRL  |
|       5 | RSHIFT |
|       6 | RALT   |
|       7 | RGUI   |
```

### Keyboard Scan Codes
```
| Byte | Name           |
|------+----------------|
| 0x00 | NOKEY          |
| 0x01 | ROLL_OVER      |
| 0x02 | POST_FAIL      |
| 0x03 | ERRUNDEF       |
| 0x04 | A              |
| 0x05 | B              |
| 0x06 | C              |
| 0x07 | D              |
| 0x08 | E              |
| 0x09 | F              |
| 0x0A | G              |
| 0x0B | H              |
| 0x0C | I              |
| 0x0D | J              |
| 0x0E | K              |
| 0x0F | L              |
| 0x10 | M              |
| 0x11 | N              |
| 0x12 | O              |
| 0x13 | P              |
| 0x14 | Q              |
| 0x15 | R              |
| 0x16 | S              |
| 0x17 | T              |
| 0x18 | U              |
| 0x19 | V              |
| 0x1A | W              |
| 0x1B | X              |
| 0x1C | Y              |
| 0x1D | Z              |
| 0x1E | 1              |
| 0x1F | 2              |
| 0x20 | 3              |
| 0x21 | 4              |
| 0x22 | 5              |
| 0x23 | 6              |
| 0x24 | 7              |
| 0x25 | 8              |
| 0x26 | 9              |
| 0x27 | 0              |
| 0x28 | ENTER          |
| 0x29 | ESCAPE         |
| 0x2A | BSPACE         |
| 0x2B | TAB            |
| 0x2C | SPACE          |
| 0x2D | MINUS          |
| 0x2E | EQUAL          |
| 0x2F | LBRACKET       |
| 0x30 | RBRACKET       |
| 0x31 | BSLASH         |
| 0x32 | NONUS_HASH     |
| 0x33 | SCOLON         |
| 0x34 | QUOTE          |
| 0x35 | GRAVE          |
| 0x36 | COMMA          |
| 0x37 | DOT            |
| 0x38 | SLASH          |
| 0x39 | CAPSLOCK       |
| 0x3A | F1             |
| 0x3B | F2             |
| 0x3C | F3             |
| 0x3D | F4             |
| 0x3E | F5             |
| 0x3F | F6             |
| 0x40 | F7             |
| 0x41 | F8             |
| 0x42 | F9             |
| 0x43 | F10            |
| 0x44 | F11            |
| 0x45 | F12            |
| 0x46 | PSCREEN        |
| 0x47 | SCKLOCK        |
| 0x48 | PAUSE          |
| 0x49 | INSERT         |
| 0x4A | HOME           |
| 0x4B | PGUP           |
| 0x4C | DELETE         |
| 0x4D | END            |
| 0x4E | PGDOWN         |
| 0x4F | RIGHT          |
| 0x50 | LEFT           |
| 0x51 | DOWN           |
| 0x52 | UP             |
| 0x53 | NUMLOCK        |
| 0x54 | KP_SLASH       |
| 0x55 | KP_ASTERISK    |
| 0x56 | KP_MINUS       |
| 0x57 | KP_PLUS        |
| 0x58 | KP_ENTER       |
| 0x59 | KP_1           |
| 0x5A | KP_2           |
| 0x5B | KP_3           |
| 0x5C | KP_4           |
| 0x5D | KP_5           |
| 0x5E | KP_6           |
| 0x5F | KP_7           |
| 0x60 | KP_8           |
| 0x61 | KP_9           |
| 0x62 | KP_0           |
| 0x63 | KP_DOT         |
| 0x64 | NON_US_BSLASH  |
| 0x65 | APPLICATION    |
| 0x66 | POWER          |
| 0x67 | KP_EQUAL       |
| 0x68 | F13            |
| 0x69 | F14            |
| 0x6A | F15            |
| 0x6B | F16            |
| 0x6C | F17            |
| 0x6D | F18            |
| 0x6E | F19            |
| 0x6F | F20            |
| 0x70 | F21            |
| 0x71 | F22            |
| 0x72 | F23            |
| 0x73 | F24            |
| 0x74 | EXECUTE        |
| 0x75 | HELP           |
| 0x76 | MENU           |
| 0x77 | SELECT         |
| 0x78 | STOP           |
| 0x79 | AGAIN          |
| 0x7A | UNDO           |
| 0x7B | CUT            |
| 0x7C | COPY           |
| 0x7D | PASTE          |
| 0x7E | FIND           |
| 0x7F | MUTE           |
| 0x80 | VOLUP          |
| 0x81 | VOLDOWN        |
| 0x82 | LOCKING_CAPS   |
| 0x83 | LOCKING_NUM    |
| 0x84 | LOCKING_SCROLL |
| 0x85 | KP_COMMA       |
| 0x86 | KP_EQUAL_SIGN  |
| 0x87 | INTERNATIONAL1 |
| 0x88 | INTERNATIONAL2 |
| 0x89 | INTERNATIONAL3 |
| 0x8A | INTERNATIONAL4 |
| 0x8B | INTERNATIONAL5 |
| 0x8C | INTERNATIONAL6 |
| 0x8D | INTERNATIONAL7 |
| 0x8E | INTERNATIONAL8 |
| 0x8F | INTERNATIONAL9 |
| 0x90 | LANG1          |
| 0x91 | LANG2          |
| 0x92 | LANG3          |
| 0x93 | LANG4          |
| 0x94 | LANG5          |
| 0x95 | LANG6          |
| 0x96 | LANG7          |
| 0x97 | LANG8          |
| 0x98 | LANG9          |
| 0x99 | ALT_ERASE      |
| 0x9A | SYSREQ         |
| 0x9B | CANCEL         |
| 0x9C | CLEAR          |
| 0x9D | PRIOR          |
| 0x9E | RETURN         |
| 0x9F | SEPARATOR      |
| 0xA0 | OUT            |
| 0xA1 | OPER           |
| 0xA2 | CLEAR_AGAIN    |
| 0xA3 | CRSEL          |
| 0xA4 | EXSEL          |
```

## Lighting
The lighting section is fairly self explanitory.
Lighting Effect uses the following definiton table:
```
| Byte | Name      |
|------+-----------|
| 0x00 | NO_EFFECT |
| 0x01 | PULSE     |
| 0x02 | RAINBOW   |
```
