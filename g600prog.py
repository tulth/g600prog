#!/bin/env python
"""Utility to read/write logitech g600 mouse key maps.
Behaves like cp, ie, give it a source and destination.
In most cases, this requires root (ie, run sudo <this script>).
Mouse configurations are stored in a human readable json format.
Note: MOUSE is a special keyword that specifies the mouse rather than a file.

For example, to copy the current mouse config to a file called mouse_config.json:
$ sudo ./g600prog.py MOUSE mouse_config.json

Copying a custom_config.json file to the mouse:
$ sudo ./g600prog.py custom_config.json MOUSE

Leaving off the second argument causes it to print to stdout.
So, to print your current mouse config:
$ sudo ./g600prog.py MOUSE"""
from __future__ import print_function
import sys
import os
import argparse
import itertools
import json
import collections
import time
import usb.core
import usb.util


def main(argv):
    cfg = parseArgs(argv)
    if cfg.SOURCE == "MOUSE":
        mouseMapping = readMouseMappingFromMouse(cfg.debug)
    else:
        mouseMapping = readMouseMappingFromFile(cfg.SOURCE, cfg.debug)
    if cfg.bytes:
        mouseMappingBytes = G600MouseMappingBytes()
        mouseMappingBytes.fromModeRawBytesList(mouseMapping.toModeRawBytesList())
        mouseMapping = mouseMappingBytes
    if cfg.DESTINATION is None:
        print(mouseMapping)
    elif cfg.DESTINATION == "MOUSE":
        writeMouseMappingToMouse(mouseMapping, cfg.debug, cfg.dry_run)
    else:
        saveMouseMappingToFile(mouseMapping, cfg.DESTINATION, cfg.overwrite_file)


def readMouseMappingFromMouse(debug):
    print("Reading mouse config from mouse...")
    mouseMapping = G600MouseMapping()
    rawModeBytesList = readUsbMouseMappingRawBytes(debug)
    mouseMapping.fromModeRawBytesList(rawModeBytesList)
    print("... done reading mouse config from mouse")
    return mouseMapping


def readMouseMappingFromFile(fileName, debug):
    print("Reading mouse config from file >{}< ...".format(fileName))
    with open(fileName, 'r') as fileHandle:
        jsonObj = json.loads(fileHandle.read())
        mouseMapping = G600MouseMapping()
        if "configFormat" not in jsonObj:
            raise FromJsonError("missing configFormat!")
        if jsonObj["configFormat"] == "BytesFormat":
            mouseMappingBytes = G600MouseMappingBytes()
            mouseMappingBytes.simpleRepr = jsonObj
            mouseMapping.fromModeRawBytesList(mouseMappingBytes.toModeRawBytesList())
        elif jsonObj["configFormat"] == "HumanReadableFormat":
            mouseMapping.simpleRepr = jsonObj
        else:
            raise FromJsonError("Undefined configFormat >>{}<<".format(jsonObj["configFormat"]))
    print("... done reading mouse config from file")
    return mouseMapping


def saveMouseMappingToFile(mouseMapping, fileName, forceWrite):
    print("Saving the mouse config to file >{}< ...".format(fileName))
    if os.path.isfile(fileName) and not forceWrite:
        raise Exception("File already exists and overwrite-file flag not set")
    with open(fileName, "w") as fileHandle:
        fileHandle.write(mouseMapping.json)
    print("...done saving the mouse config to file")


def writeMouseMappingToMouse(mouseMapping, debug, dryRun):
    print("Writing the mouse config to the mouse...")
    rawModeBytesList = mouseMapping.toModeRawBytesList()
    writeUsbMouseMappingRawBytes(rawModeBytesList, debug, dryRun)
    print("...done writing read mouse config to the mouse")


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    if len(argv) == 1:
        argv.append('-h')

    parser.add_argument('SOURCE',
                        help='Configuration source, can be MOUSE for the mouse itself or a filename.',)
    parser.add_argument('DESTINATION', nargs='?', default=None,
                        help='Optional configuration destination, can be the MOUSE or filename.  If omitted, prints to stdout.',)
    parser.add_argument('-f', '--overwrite-file',
                        help='Normally, if the destination file already exists, the program will terminate.  This option forces the overwrite of DESTINATION even if it exists.',
                        action='store_true',)
    parser.add_argument('-n', '--dry-run',
                        help='For testing writes to the mouse, intended to be used in conjunction with debug, will do everything except for actually send the usb programming messages.',
                        action='store_true',)
    parser.add_argument('-d', '--debug',
                        help='Turn on debug printing.',
                        action='store_true',)
    parser.add_argument('--bytes',
                        help='Store output config in JSON byte array format.  This could be useful for moving betweeen versions of this app where the human readable JSON format changes.',
                        action='store_true',)

    cfg = parser.parse_args()
    return cfg

################################################################################
# usb read/write to the mouse control interface.
# Operates on a 3 element sequence where each element is a bytearray()
IDVENDOR = 0x046d
IDPRODUCT = 0xc24a
G600_CONTROL_INTERFACE = 1
G600_REPORT_IDS = (0x03f3, 0x03f4, 0x03f5)  # one for each of the three mouse "modes"

G600_READ_REQTYPE = 0xA1
G600_READ_REQ = 0x01
G600_READ_IDX = G600_CONTROL_INTERFACE
G600_READ_LENGTH = 154


def readUsbMouseMappingRawBytes(debug=False):
    """Returns three element list.
    One for each of the mouse "modes."
    Each list element is a bytearray() type.
    """
    if debug:
        print("About to read USB...")
    dev = usb.core.find(idVendor=IDVENDOR, idProduct=IDPRODUCT)
    if dev.is_kernel_driver_active(G600_CONTROL_INTERFACE) is True:
        # tell the kernel to detach
        dev.detach_kernel_driver(G600_CONTROL_INTERFACE)
        # claim the device
        usb.util.claim_interface(dev, G600_CONTROL_INTERFACE)
    modes = []
    for reportId in G600_REPORT_IDS:
        replyMsg = dev.ctrl_transfer(bmRequestType=G600_READ_REQTYPE,  # this means control
                                     bRequest=G600_READ_REQ,
                                     wValue=reportId,
                                     wIndex=G600_READ_IDX,
                                     data_or_wLength=G600_READ_LENGTH,
                                     timeout=None)
        if debug:
            print("for reportId=0x{:04x}, read these bytes: ".format(reportId),)
            print(" ".join("0x{:02x}".format(x) for x in replyMsg))
        modes.append(replyMsg)
    # release the device
    usb.util.release_interface(dev, G600_CONTROL_INTERFACE)
    # reattach the device to the OS kernel
    dev.attach_kernel_driver(G600_CONTROL_INTERFACE)
    # done
    if debug:
        print("...Done reading USB")
    return modes

G600_WRITE_REQTYPE = 0x21
G600_WRITE_REQ = 0x09
G600_WRITE_IDX = G600_CONTROL_INTERFACE


def writeUsbMouseMappingRawBytes(modes, debug=False, dryRun=True):
    """Argument should be a three element list.
    One for each of the mouse "modes."
    Each list element is a bytearray() type.
    """
    if debug:
        print("About to write USB...")
    dev = usb.core.find(idVendor=IDVENDOR, idProduct=IDPRODUCT)
    if dev.is_kernel_driver_active(G600_CONTROL_INTERFACE) is True:
        # tell the kernel to detach
        dev.detach_kernel_driver(G600_CONTROL_INTERFACE)
        # claim the device
        usb.util.claim_interface(dev, G600_CONTROL_INTERFACE)
    for reportId, rawBytes in zip(G600_REPORT_IDS, modes):
        if debug:
            print("for reportId=0x{:04x}, sending these bytes: ".format(reportId),)
            print(" ".join("0x{:02x}".format(x) for x in rawBytes))
        if dryRun:
            print("dryRun flag set, not sending usb config write message")
        else:
            l = dev.ctrl_transfer(bmRequestType=G600_WRITE_REQTYPE,  # this means control
                                  bRequest=G600_WRITE_REQ,
                                  wValue=reportId,
                                  wIndex=G600_WRITE_IDX,
                                  data_or_wLength=rawBytes,
                                  timeout=None)
            assert l == len(rawBytes)
            time.sleep(1.1)
    # release the device
    usb.util.release_interface(dev, G600_CONTROL_INTERFACE)
    # reattach the device to the OS kernel
    dev.attach_kernel_driver(G600_CONTROL_INTERFACE)
    if debug:
        print("...Done writing USB")
    # done
################################################################################

################################################################################
# raw scan code maps of known codes


def invMap(mapDict):
    return {v: k for k, v in mapDict.items()}

MOUSE_SCAN_CODES_DICT = {0x00: "NO_MOUSEBUT",
                         0x01: "LEFT_CLICK",
                         0x02: "RIGHT_CLICK",
                         0x03: "MIDDLE_CLICK",
                         0x04: "BACK",
                         0x05: "FORWARD",
                         0x06: "MOUSE6",
                         0x07: "MOUSE7",
                         0x11: "DPI_UP",
                         0x12: "DPI_DOWN",
                         0x13: "DPI_CYCLING",
                         0x14: "MODE_SWITCH",
                         0x15: "DPI_SHIFT",
                         0x16: "DPI_DEFAULT",
                         0x17: "GSHIFT",
                         }
MOUSE_SCAN_CODES_INVDICT = invMap(MOUSE_SCAN_CODES_DICT)  # for reverse lookup

KB_MODIFIER_BIT_CODES_DICT = {0: "LCTRL",
                              1: "LSHIFT",
                              2: "LALT",
                              3: "LGUI",
                              4: "RCTRL",
                              5: "RSHIFT",
                              6: "RALT",
                              7: "RGUI",
                              }
KB_MODIFIER_BIT_CODES_INVDICT = invMap(KB_MODIFIER_BIT_CODES_DICT)  # for reverse lookup

KB_SCAN_CODES_DICT = {0x00: "NOKEY",
                      0x01: "ROLL_OVER",
                      0x02: "POST_FAIL",
                      0x03: "UNDEF",
                      0x04: "A",
                      0x05: "B",
                      0x06: "C",
                      0x07: "D",
                      0x08: "E",
                      0x09: "F",
                      0x0A: "G",
                      0x0B: "H",
                      0x0C: "I",
                      0x0D: "J",
                      0x0E: "K",
                      0x0F: "L",
                      0x10: "M",
                      0x11: "N",
                      0x12: "O",
                      0x13: "P",
                      0x14: "Q",
                      0x15: "R",
                      0x16: "S",
                      0x17: "T",
                      0x18: "U",
                      0x19: "V",
                      0x1A: "W",
                      0x1B: "X",
                      0x1C: "Y",
                      0x1D: "Z",
                      0x1E: "1",
                      0x1F: "2",
                      0x20: "3",
                      0x21: "4",
                      0x22: "5",
                      0x23: "6",
                      0x24: "7",
                      0x25: "8",
                      0x26: "9",
                      0x27: "0",
                      0x28: "ENTER",
                      0x29: "ESCAPE",
                      0x2A: "BSPACE",
                      0x2B: "TAB",
                      0x2C: "SPACE",
                      0x2D: "MINUS",
                      0x2E: "EQUAL",
                      0x2F: "LBRACKET",
                      0x30: "RBRACKET",
                      0x31: "BSLASH",
                      0x32: "NONUS_HASH",
                      0x33: "SCOLON",
                      0x34: "QUOTE",
                      0x35: "GRAVE",
                      0x36: "COMMA",
                      0x37: "DOT",
                      0x38: "SLASH",
                      0x39: "CAPSLOCK",
                      0x3A: "F1",
                      0x3B: "F2",
                      0x3C: "F3",
                      0x3D: "F4",
                      0x3E: "F5",
                      0x3F: "F6",
                      0x40: "F7",
                      0x41: "F8",
                      0x42: "F9",
                      0x43: "F10",
                      0x44: "F11",
                      0x45: "F12",
                      0x46: "PSCREEN",
                      0x47: "SCKLOCK",
                      0x48: "PAUSE",
                      0x49: "INSERT",
                      0x4A: "HOME",
                      0x4B: "PGUP",
                      0x4C: "DELETE",
                      0x4D: "END",
                      0x4E: "PGDOWN",
                      0x4F: "RIGHT",
                      0x50: "LEFT",
                      0x51: "DOWN",
                      0x52: "UP",
                      0x53: "NUMLOCK",
                      0x54: "KP_SLASH",
                      0x55: "KP_ASTERISK",
                      0x56: "KP_MINUS",
                      0x57: "KP_PLUS",
                      0x58: "KP_ENTER",
                      0x59: "KP_1",
                      0x5A: "KP_2",
                      0x5B: "KP_3",
                      0x5C: "KP_4",
                      0x5D: "KP_5",
                      0x5E: "KP_6",
                      0x5F: "KP_7",
                      0x60: "KP_8",
                      0x61: "KP_9",
                      0x62: "KP_0",
                      0x63: "KP_DOT",
                      0x64: "NONUS_BSLASH",
                      0x65: "APPLICATION",
                      0x66: "POWER",
                      0x67: "KP_EQUAL",
                      0x68: "F13",
                      0x69: "F14",
                      0x6A: "F15",
                      0x6B: "F16",
                      0x6C: "F17",
                      0x6D: "F18",
                      0x6E: "F19",
                      0x6F: "F20",
                      0x70: "F21",
                      0x71: "F22",
                      0x72: "F23",
                      0x73: "F24",
                      0x74: "EXECUTE",
                      0x75: "HELP",
                      0x76: "MENU",
                      0x77: "SELECT",
                      0x78: "STOP",
                      0x79: "AGAIN",
                      0x7A: "UNDO",
                      0x7B: "CUT",
                      0x7C: "COPY",
                      0x7D: "PASTE",
                      0x7E: "FIND",
                      0x7F: "MUTE",
                      0x80: "VOLUP",
                      0x81: "VOLDOWN",
                      0x82: "LOCKING_CAPS",
                      0x83: "LOCKING_NUM",
                      0x84: "LOCKING_SCROLL",
                      0x85: "KP_COMMA",
                      0x86: "KP_EQUAL_AS400",
                      0x87: "INT1",
                      0x88: "INT2",
                      0x89: "INT3",
                      0x8A: "INT4",
                      0x8B: "INT5",
                      0x8C: "INT6",
                      0x8D: "INT7",
                      0x8E: "INT8",
                      0x8F: "INT9",
                      0x90: "LANG1",
                      0x91: "LANG2",
                      0x92: "LANG3",
                      0x93: "LANG4",
                      0x94: "LANG5",
                      0x95: "LANG6",
                      0x96: "LANG7",
                      0x97: "LANG8",
                      0x98: "LANG9",
                      0x99: "ALT_ERASE",
                      0x9A: "SYSREQ",
                      0x9B: "CANCEL",
                      0x9C: "CLEAR",
                      0x9D: "PRIOR",
                      0x9E: "RETURN",
                      0x9F: "SEPARATOR",
                      0xA0: "OUT",
                      0xA1: "OPER",
                      0xA2: "CLEAR_AGAIN",
                      0xA3: "CRSEL",
                      0xA4: "EXSEL",
                      }
KB_SCAN_CODES_INVDICT = invMap(KB_SCAN_CODES_DICT)  # for reverse lookup

LIGHTING_EFFECT_DICT = {0x00: "NO_EFFECT",
                        0x01: "PULSE",
                        0x02: "RAINBOW",
                        }
LIGHTING_EFFECT_INVDICT = invMap(LIGHTING_EFFECT_DICT)  # for reverse lookup
################################################################################

################################################################################
# basic classes that go to/from:
#   bytearray
#   json string
#   simple representable types (array, ordered dict, integer, string)
# types here:
#   * singleByte
#   * homogeneous array
#   * heterogeneous ordered dict
constant0ByteIter = itertools.repeat(0)


class MappingBuildError(Exception):
    pass


class FromJsonError(Exception):
    pass


class BaseFieldType(object):
    """Base type the other classes, do not use this class directly"""
    ID = "BaseField"
    JSON_INDENT = 4

    def __init__(self, byteArray=constant0ByteIter, id=None):
        super(BaseFieldType, self).__init__()  # python2 compatibility
        self.id = self.ID if id is None else id

    def __str__(self):
        return self.json

    def toJson(self):
        return json.dumps(self.simpleRepr, indent=self.JSON_INDENT)

    def fromJson(self, jsonStr):
        try:
            self.simpleRepr = json.loads(jsonStr)
        except MappingBuildError as err:
            errStr = "{id}: Unable to build from json string; ".format(id=self.id)
            raise FromJsonError(errStr + str(err)) from err

    json = property(toJson, fromJson)


class SingleByteFieldType(BaseFieldType):
    ID = "SingleByteField"

    def __init__(self, byteArray=constant0ByteIter, id=None):
        super(SingleByteFieldType, self).__init__(byteArray, id)  # python2 compatibility
        self.bytes = byteArray

    def toByteArray(self):
        return bytearray([self._b])

    def fromByteArray(self, byteArray):
        for i, byte in zip(range(1), iter(byteArray)):
            if byte in range(0, 256):
                self._b = byte
            else:
                errStr = "{id}: byte must be in range(0, 256)".format(id=self.id)
                raise MappingBuildError(errStr)

    def toSimpleRepr(self):
        return self._b

    def fromSimpleRepr(self, arg):
        try:
            bArr = bytearray([arg])
        except ValueError as err:
            errStr = "{id}: ".format(id=self.id)
            raise MappingBuildError(errStr + str(err)) from err
        self.fromByteArray(bArr)

    bytes = property(toByteArray, fromByteArray)
    simpleRepr = property(toSimpleRepr, fromSimpleRepr)


class ArrayFieldType(BaseFieldType):
    ID = "ArrayField"
    NUM_ELEM = 2
    ELEM_TYPE = SingleByteFieldType
    ERR_FMT_PREFIX = "{id}[{index}]=>"

    def __init__(self, byteArray=constant0ByteIter, id=None, numElem=None, elemType=None, ):
        super(ArrayFieldType, self).__init__()  # python2 compatibility
        self.id = self.ID if id is None else id
        self.numElem = self.NUM_ELEM if numElem is None else numElem
        self.elemType = self.ELEM_TYPE if elemType is None else elemType
        self.elemList = []
        byteArrayIter = iter(byteArray)
        for i in range(self.numElem):
            self.elemList.append(self.elemType(byteArrayIter))

    def toByteArray(self):
        retVal = bytearray()
        for elem in self.elemList:
            retVal.extend(elem.bytes)
        return retVal

    def fromByteArray(self, byteArray):
        byteArrayIter = iter(byteArray)
        for elem in self.elemList:
            elem.bytes = byteArrayIter

    def toSimpleRepr(self):
        return [field.simpleRepr for field in self.elemList]

    def _assertArraySane(self, arg):
        if len(self.elemList) != len(arg):
            errStr = self.ERR_FMT_PREFIX.format(id=self.id, index="")
            errStr += "array length mismatch: expected {expectLen} elements, saw {actualLen} elements"
            errStr = errStr.format(id=self.id, expectLen=len(self.elemList), actualLen=len(arg))
            raise MappingBuildError(errStr)

    def fromSimpleRepr(self, arg):
        self._assertArraySane(arg)
        for index, elem in enumerate(self.elemList):
            try:
                elem.simpleRepr = arg[index]
            except MappingBuildError as err:
                prependStr = self.ERR_FMT_PREFIX.format(id=self.id, index=index)
                err.args = (prependStr + err.args[0],) + err.args[1:]
                raise err

    bytes = property(toByteArray, fromByteArray)
    simpleRepr = property(toSimpleRepr, fromSimpleRepr)


class CompositeFieldType(BaseFieldType):
    ID = "CompositeField"
    KTM = [("f1", SingleByteFieldType), ("f2", SingleByteFieldType)]
    ERR_FMT_PREFIX = "{id}[{field}]=>"

    def __init__(self, byteArray=constant0ByteIter, id=None, keyToTypeMap=None, ):
        super(CompositeFieldType, self).__init__()
        self.id = self.ID if id is None else id
        self.keyToTypeMap = collections.OrderedDict(self.KTM) if keyToTypeMap is None else collections.OrderedDict(keyToTypeMap)
        self.elemDict = collections.OrderedDict()
        byteArrayIter = iter(byteArray)
        for fieldId in self.keyToTypeMap:
            self.elemDict[fieldId] = self.keyToTypeMap[fieldId](byteArrayIter)

    def toByteArray(self):
        retVal = bytearray()
        for fieldId in self.elemDict:
            retVal.extend(self.elemDict[fieldId].bytes)
        return retVal

    def fromByteArray(self, byteArray):
        byteArrayIter = iter(byteArray)
        for fieldId in self.elemDict:
            self.elemDict[fieldId].bytes = byteArrayIter

    def toSimpleRepr(self):
        simpleDict = collections.OrderedDict()
        for fieldId in self.elemDict:
            simpleDict[fieldId] = self.elemDict[fieldId].toSimpleRepr()
        return simpleDict

    def _assertFieldsSane(self, arg):
        missingFields = set(self.elemDict.keys()) - set(arg.keys())
        extraFields = set(arg.keys()) - set(self.elemDict.keys())
        if len(missingFields) > 0:
            errStr = self.ERR_FMT_PREFIX.format(id=self.id, field="")
            errStr += "missing fields: {missing}, extra fields {extra}".format(missing=missingFields,
                                                                               extra=extraFields)
            raise MappingBuildError(errStr)

    def fromSimpleRepr(self, arg):
        self._assertFieldsSane(arg)
        for fieldId in self.elemDict:
            try:
                self.elemDict[fieldId].fromSimpleRepr(arg[fieldId])
            except MappingBuildError as err:
                prependStr = self.ERR_FMT_PREFIX.format(id=self.id, field=fieldId)
                err.args = (prependStr + err.args[0],) + err.args[1:]
                raise err

    bytes = property(toByteArray, fromByteArray)
    simpleRepr = property(toSimpleRepr, fromSimpleRepr)
################################################################################

################################################################################
# derived g600 config field types


def cleanStr(arg):
    return arg.strip().upper()


def convertErr(arg, id):
    raise MappingBuildError("{} unable to convert representation of {}".format(id, arg))


def undefinedConvert(arg, id):
    u = "UNDEFINED"
    argClean = cleanStr(arg)
    if argClean[0:len(u)] != u:
        raise convertErr(arg, id)
    for char in argClean[len(u):]:
        if char not in "0123456789":
            raise convertErr(arg, id)
    return int(argClean[len(u):])


class G600MouseScanCodeType(SingleByteFieldType):
    ID = "mouseScanCode"

    def toSimpleRepr(self):
        b = self.bytes[0]
        if b in MOUSE_SCAN_CODES_DICT:
            return MOUSE_SCAN_CODES_DICT[b]
        else:
            return "UNDEFINED{:03d}".format(b)

    def fromSimpleRepr(self, arg):
        argClean = cleanStr(arg)
        if argClean in MOUSE_SCAN_CODES_INVDICT:
            b = MOUSE_SCAN_CODES_INVDICT[argClean]
        else:
            b = undefinedConvert(argClean, self.id)
        self.bytes = [b]


class KbModifierBitWiseType(SingleByteFieldType):
    ID = "kbModifier"

    def toSimpleRepr(self):
        b = self.bytes[0]
        codes = []
        for idx, bit in enumerate(reversed("{:08b}".format(b))):
            if bit == "1":
                codes.append(KB_MODIFIER_BIT_CODES_DICT[idx])
        retVal = "+".join(codes)
        if retVal == "":
            retVal = "NO_MOD"
        return retVal

    def fromSimpleRepr(self, arg):
        argClean = cleanStr(arg)
        b = 0
        if argClean == "NO_MOD":
            pass
        else:
            modifierCodeList = argClean.split("+")
            for modifierCode in modifierCodeList:
                if modifierCode not in KB_MODIFIER_BIT_CODES_INVDICT:
                    convertErr(modifierCode, self.id)
                else:
                    b += 2 ** (KB_MODIFIER_BIT_CODES_INVDICT[modifierCode])
        self.bytes = [b]


class KbScanCodeType(SingleByteFieldType):
    ID = "kbScanCode"

    def toSimpleRepr(self):
        b = self.bytes[0]
        if b in KB_SCAN_CODES_DICT:
            return KB_SCAN_CODES_DICT[b]
        else:
            return "UNDEFINED{:03d}".format(b)

    def fromSimpleRepr(self, arg):
        argClean = cleanStr(arg)
        if argClean in KB_SCAN_CODES_INVDICT:
            b = KB_SCAN_CODES_INVDICT[argClean]
        else:
            b = undefinedConvert(argClean, self.id)
        self.bytes = [b]


class G600PollRateType(SingleByteFieldType):
    ID = "pollRate"

    def calcDerivedPollRate(self, b):
        derivedPollRate = int(1000 / (1 + int(b)))
        return derivedPollRate

    def toSimpleRepr(self):
        b = self.bytes[0]
        return self.calcDerivedPollRate(b)

    def fromSimpleRepr(self, arg):
        b = int((1000 // int(arg)) - 1)
        if b < 0:
            b = 0
        if b > 255:
            b = 255
        argActual = self.calcDerivedPollRate(b)
        if argActual != arg:
            print("Warning! Requested pollrate of {} resulted in a actual pollrate of {}".format(arg, argActual))
        self.bytes = [b]


class G600DPIType(SingleByteFieldType):
    ID = "dpi"

    def calcDerivedDpi(self, b):
        derivedDpi = 50 * b
        return derivedDpi

    def toSimpleRepr(self):
        b = self.bytes[0]
        return self.calcDerivedDpi(b)

    def fromSimpleRepr(self, arg):
        b = int((arg) // 50)
        if b < 0:
            b = 0
        if b > 255:
            b = 255
        if arg != 0 and b == 0:
            b = 1
        argActual = self.calcDerivedDpi(b)
        if argActual != arg:
            print("Warning! Requested dpi of {} resulted in a actual dpi of {}".format(arg, argActual))
        self.bytes = [b]


class G600MouseButtonActionType(CompositeFieldType):
    KTM = [(G600MouseScanCodeType.ID, G600MouseScanCodeType),
           (KbModifierBitWiseType.ID, KbModifierBitWiseType),
           (KbScanCodeType.ID, KbScanCodeType),
           ]


class G600DPIGroupType(CompositeFieldType):
    KTM = [('DPI_SHIFT DPI', G600DPIType),
           ('DefaultDPIIndex', SingleByteFieldType),
           ('DPI1', G600DPIType),
           ('DPI2', G600DPIType),
           ('DPI3', G600DPIType),
           ('DPI4', G600DPIType),
           ]


class G600LightingEffectType(SingleByteFieldType):
    ID = "lightingEffect"

    def toSimpleRepr(self):
        b = self.bytes[0]
        if b in LIGHTING_EFFECT_DICT:
            return LIGHTING_EFFECT_DICT[b]
        else:
            return "UNDEFINED{:03d}".format(b)

    def fromSimpleRepr(self, arg):
        argClean = cleanStr(arg)
        if argClean in LIGHTING_EFFECT_INVDICT:
            b = LIGHTING_EFFECT_INVDICT[argClean]
        else:
            b = undefinedConvert(argClean, self.id)
        self.bytes = [b]


class G600LightingType(CompositeFieldType):
    ID = "Lighting"
    KTM = [("Lighting Effect", G600LightingEffectType),
           ("Lighting Change Rate (0-15)", SingleByteFieldType),
           ]


class G600LedColorsType(CompositeFieldType):
    KTM = [('Red', SingleByteFieldType),
           ('Green', SingleByteFieldType),
           ('Blue', SingleByteFieldType),
           ]


class G600ButtonMapType(CompositeFieldType):
    ID = "ButtonMap"
    KTM = [('g1 (left button)', G600MouseButtonActionType),
           ('g2 (right button)', G600MouseButtonActionType),
           ('g3 (middle button)', G600MouseButtonActionType),
           ('g4 (mousewheel left)', G600MouseButtonActionType),
           ('g5 (mousewheel right)', G600MouseButtonActionType),
           ('g6 (side/gshift)', G600MouseButtonActionType),
           ('g7 (button back)', G600MouseButtonActionType),
           ('g8 (button forward)', G600MouseButtonActionType),
           ('g9 (side buttonpad)', G600MouseButtonActionType),
           ('g10 (side buttonpad)', G600MouseButtonActionType),
           ('g11 (side buttonpad)', G600MouseButtonActionType),
           ('g12 (side buttonpad)', G600MouseButtonActionType),
           ('g13 (side buttonpad)', G600MouseButtonActionType),
           ('g14 (side buttonpad)', G600MouseButtonActionType),
           ('g15 (side buttonpad)', G600MouseButtonActionType),
           ('g16 (side buttonpad)', G600MouseButtonActionType),
           ('g17 (side buttonpad)', G600MouseButtonActionType),
           ('g18 (side buttonpad)', G600MouseButtonActionType),
           ('g19 (side buttonpad)', G600MouseButtonActionType),
           ('g20 (side buttonpad)', G600MouseButtonActionType),
           ]
    ELEM_TYPE = G600MouseButtonActionType


class UnknownBytesArray0(ArrayFieldType):
    ID = "Unknown"
    NUM_ELEM = 0x4b - 0x46
    ELEM_TYPE = SingleByteFieldType


class UnknownBytesArray1(ArrayFieldType):
    ID = "Unknown"
    NUM_ELEM = 0x5f - 0x52
    ELEM_TYPE = SingleByteFieldType


class G600ModeMouseMappingType(CompositeFieldType):
    ID = "ConfigMode"
    KTM = [("LedColorsNormal", G600LedColorsType),
           ("Lighting", G600LightingType),
           ("Unknown0", UnknownBytesArray0),
           ("PollRate", G600PollRateType),
           ("DPI", G600DPIGroupType),
           ("Unknown1", UnknownBytesArray1),
           ("buttonMapNormal", G600ButtonMapType),
           ("LedColorsShifted", G600LedColorsType),
           ("buttonMapShifted", G600ButtonMapType),
           ]


class StringField(BaseFieldType):
    ID = "StringField"

    def toByteArray(self):
        return bytearray([])

    def fromByteArray(self, byteArray):
        pass

    def toSimpleRepr(self):
        return self.id

    def fromSimpleRepr(self, arg):
        pass


class G600HumanReadableFormatType(StringField):
    ID = "HumanReadableFormat"


class G600BytesFormatType(StringField):
    ID = "BytesFormat"


class G600MouseMapping(CompositeFieldType):
    ID = "MouseMapping"
    KTM = [("Mode1 (default)", G600ModeMouseMappingType),
           ("Mode2", G600ModeMouseMappingType),
           ("Mode3", G600ModeMouseMappingType),
           ("configFormat", G600HumanReadableFormatType),
           ]

    def toModeRawBytesList(self):
        """Returns three element list.
        One for each of the mouse "modes."
        Each list element is a bytearray() type suitable for
        sending over usb to program the g600 config interface
        """
        modeRawBytesList = []
        for reportId, elemKey in zip(G600_REPORT_IDS, self.elemDict):
            rawBytes = bytearray([reportId & 0xff])
            rawBytes.extend(self.elemDict[elemKey].bytes)
            modeRawBytesList.append(rawBytes)
        return modeRawBytesList

    def fromModeRawBytesList(self, modeRawBytesList):
        """Argument should be a three element list.
        One for each of the mouse "modes."
        Each list element is a bytearray() type, read directly
        from the g600 config interface
        """
        for modeRawBytes, elemKey in zip(modeRawBytesList, self.elemDict):
            self.elemDict[elemKey].bytes = modeRawBytes[0x1:]

    def toByteArray(self):
        raise NotImplementedError()

    def fromByteArray(self, byteArray):
        raise NotImplementedError()

    bytes = property(toByteArray, fromByteArray)


class G600BytesModeMouseMappingType(ArrayFieldType):
    ID = "BytesMouseMapping"
    NUM_ELEM = G600_READ_LENGTH - 1


class G600MouseMappingBytes(G600MouseMapping):
    ID = "MouseMappingBytes"
    KTM = [("Mode1 (default)", G600BytesModeMouseMappingType),
           ("Mode2", G600BytesModeMouseMappingType),
           ("Mode3", G600BytesModeMouseMappingType),
           ("configFormat", G600BytesFormatType),
           ]

################################################################################

if __name__ == '__main__':
    main(sys.argv)
