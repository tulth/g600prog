#!/bin/env python
from __future__ import print_function
import sys
import argparse
import itertools
import json
import collections

IDVENDOR = 0x046d
IDPRODUCT = 0xc24a
G600_CONTROL_INTERFACE = 1
G600_REPORT_IDS = (0x03f3, 0x03f4, 0x03f5)

def main(argv):
    cfg = parseArgs(argv)
    print(cfg)  # DELETEME
    if cfg.print_mapping or (cfg.save_mapping is not None):
        mouseMapping = readMouseMapping()
        if cfg.print_mapping:
            print(mouseMapping)
        if (cfg.save_mapping is not None):
            writeMouseMappingToFile(cfg.save_mapping)
    if cfg.write_mapping is not None:
        writeFileMappingToMouse(cfg.write_mapping)


def parseArgs(argv):
    parser = argparse.ArgumentParser(description='Utility to read/write logitech g600 mouse key maps.  In most cases, this requires root (ie, run sudo <this script>)')
    rdWrGroup = parser.add_mutually_exclusive_group()
    parser.add_argument('-p', '--print-mapping',
                        help='Print the current mappings stored in the mouse',
                        action='store_true',)
    rdWrGroup.add_argument('-s', '--save-mapping',
                           type=argparse.FileType('w'),
                           help='Save current mappings stored in the mouse to the file specified',
    )
    rdWrGroup.add_argument('-w', '--write-mapping',
                           type=argparse.FileType('r'),
                           help='Write the settings in the specified mouse mappings settings file to the mouse',
    )

    cfg = parser.parse_args()
    return cfg

def readMouseMapping():
    rawBytes = readUsbMouseMappingRawBytes(IDVENDOR, IDPRODUCT, )
    # print(" ".join("{:02x}".format(x) for x in rawBytes))  # uncomment this to hexdump the byte array
    print("readMouseMapping")  # DELETEME

def writeMouseMappingToFile(fileHandle):
    print("writeMouseMappingToFile(fileHandle")  # DELETEME

def writeFileMappingToMouse(fileHandle):
    print("writeFileMappingToMouse(fileHandle")  # DELETEME


G600_READ_REQTYPE = 0xA1
G600_READ_REQ = 0x01
G600_READ_IDX = G600_CONTROL_INTERFACE
G600_READ_LENGTH = 154
def readUsbMouseMappingRawBytes(IDVENDOR, IDPRODUCT):
    import usb.core
    import usb.util

    dev = usb.core.find(idVendor=IDVENDOR, idProduct=IDPRODUCT)
    G600_CONTROL_INTERFACE = 1

    if dev.is_kernel_driver_active(G600_CONTROL_INTERFACE) is True:
        # tell the kernel to detach
        dev.detach_kernel_driver(G600_CONTROL_INTERFACE)
        # claim the device
        usb.util.claim_interface(dev, G600_CONTROL_INTERFACE)

    mappingRawBytes = bytearray()
    for reportId in G600_REPORT_IDS:
        replyMsg = dev.ctrl_transfer(bmRequestType=G600_READ_REQTYPE, # this means control
                                     bRequest=G600_READ_REQ,
                                     wValue=reportId,
                                     wIndex=G600_READ_IDX,
                                     data_or_wLength=G600_READ_LENGTH,
                                     timeout=None)
        # print(" ".join("{:02x}".format(x) for x in replyMsg))  # uncomment this to hexdump the usb reply
        mappingRawBytes.extend(replyMsg)
    # release the device
    usb.util.release_interface(dev, G600_CONTROL_INTERFACE)
    # reattach the device to the OS kernel
    dev.attach_kernel_driver(G600_CONTROL_INTERFACE)

    return mappingRawBytes

################################################################################
## raw scan code maps of known codes
MOUSE_SCAN_CODES_DICT = {0x00  :  "NO_MOUSEBUT" ,
                         0x01  :  "LEFT_CLICK"  ,
                         0x02  :  "RIGHT_CLICK" ,
                         0x03  :  "MIDDLE_CLICK",
                         0x04  :  "BACK"        ,
                         0x05  :  "FORWARD"     ,
                         0x06  :  "MOUSE6"      ,
                         0x07  :  "MOUSE7"      ,
                         0x11  :  "DPI_UP"      ,
                         0x12  :  "DPI_DOWN"    ,
                         0x13  :  "DPI_CYCLING" ,
                         0x14  :  "MODE_SWITCH" ,
                         0x15  :  "DPI_SHIFT"   ,
                         0x16  :  "DPI_DEFAULT" ,
                         0x17  :  "GSHIFT"      ,
}

KB_MODIFIER_BIT_CODES_DICT = {0  : "KC_LCTRL"   ,
                              1  : "KC_LSHIFT"  ,
                              2  : "KC_LALT"    ,
                              3  : "KC_LGUI"    ,
                              4  : "KC_RCTRL"   ,
                              5  : "KC_RSHIFT"  ,
                              6  : "KC_RALT"    ,
                              7  : "KC_RGUI"    ,
}

KB_SCAN_CODES_DICT = {
    0x00 : "KC_NO",
    0x01 : "KC_ROLL_OVER",
    0x02 : "KC_POST_FAIL",
    0x03 : "KC_UNDEFINED",
    0x04 : "KC_A",
    0x05 : "KC_B",
    0x06 : "KC_C",
    0x07 : "KC_D",
    0x08 : "KC_E",
    0x09 : "KC_F",
    0x0A : "KC_G",
    0x0B : "KC_H",
    0x0C : "KC_I",
    0x0D : "KC_J",
    0x0E : "KC_K",
    0x0F : "KC_L",
    0x10 : "KC_M",
    0x11 : "KC_N",
    0x12 : "KC_O",
    0x13 : "KC_P",
    0x14 : "KC_Q",
    0x15 : "KC_R",
    0x16 : "KC_S",
    0x17 : "KC_T",
    0x18 : "KC_U",
    0x19 : "KC_V",
    0x1A : "KC_W",
    0x1B : "KC_X",
    0x1C : "KC_Y",
    0x1D : "KC_Z",
    0x1E : "KC_1",
    0x1F : "KC_2",
    0x20 : "KC_3",
    0x21 : "KC_4",
    0x22 : "KC_5",
    0x23 : "KC_6",
    0x24 : "KC_7",
    0x25 : "KC_8",
    0x26 : "KC_9",
    0x27 : "KC_0",
    0x28 : "KC_ENTER",
    0x29 : "KC_ESCAPE",
    0x2A : "KC_BSPACE",
    0x2B : "KC_TAB",
    0x2C : "KC_SPACE",
    0x2D : "KC_MINUS",
    0x2E : "KC_EQUAL",
    0x2F : "KC_LBRACKET",
    0x30 : "KC_RBRACKET",
    0x31 : "KC_BSLASH",
    0x32 : "KC_NONUS_HASH",
    0x33 : "KC_SCOLON",
    0x34 : "KC_QUOTE",
    0x35 : "KC_GRAVE",
    0x36 : "KC_COMMA",
    0x37 : "KC_DOT",
    0x38 : "KC_SLASH",
    0x39 : "KC_CAPSLOCK",
    0x3A : "KC_F1",
    0x3B : "KC_F2",
    0x3C : "KC_F3",
    0x3D : "KC_F4",
    0x3E : "KC_F5",
    0x3F : "KC_F6",
    0x40 : "KC_F7",
    0x41 : "KC_F8",
    0x42 : "KC_F9",
    0x43 : "KC_F10",
    0x44 : "KC_F11",
    0x45 : "KC_F12",
    0x46 : "KC_PSCREEN",
    0x47 : "KC_SCKLOCK",
    0x48 : "KC_PAUSE",
    0x49 : "KC_INSERT",
    0x4A : "KC_HOME",
    0x4B : "KC_PGUP",
    0x4C : "KC_DELETE",
    0x4D : "KC_END",
    0x4E : "KC_PGDOWN",
    0x4F : "KC_RIGHT",
    0x50 : "KC_LEFT",
    0x51 : "KC_DOWN",
    0x52 : "KC_UP",
    0x53 : "KC_NUMLOCK",
    0x54 : "KC_KP_SLASH",
    0x55 : "KC_KP_ASTERISK",
    0x56 : "KC_KP_MINUS",
    0x57 : "KC_KP_PLUS",
    0x58 : "KC_KP_ENTER",
    0x59 : "KC_KP_1",
    0x5A : "KC_KP_2",
    0x5B : "KC_KP_3",
    0x5C : "KC_KP_4",
    0x5D : "KC_KP_5",
    0x5E : "KC_KP_6",
    0x5F : "KC_KP_7",
    0x60 : "KC_KP_8",
    0x61 : "KC_KP_9",
    0x62 : "KC_KP_0",
    0x63 : "KC_KP_DOT",
    0x64 : "KC_NONUS_BSLASH",
    0x65 : "KC_APPLICATION",
    0x66 : "KC_POWER",
    0x67 : "KC_KP_EQUAL",
    0x68 : "KC_F13",
    0x69 : "KC_F14",
    0x6A : "KC_F15",
    0x6B : "KC_F16",
    0x6C : "KC_F17",
    0x6D : "KC_F18",
    0x6E : "KC_F19",
    0x6F : "KC_F20",
    0x70 : "KC_F21",
    0x71 : "KC_F22",
    0x72 : "KC_F23",
    0x73 : "KC_F24",
    0x74 : "KC_EXECUTE",
    0x75 : "KC_HELP",
    0x76 : "KC_MENU",
    0x77 : "KC_SELECT",
    0x78 : "KC_STOP",
    0x79 : "KC_AGAIN",
    0x7A : "KC_UNDO",
    0x7B : "KC_CUT",
    0x7C : "KC_COPY",
    0x7D : "KC_PASTE",
    0x7E : "KC_FIND",
    0x7F : "KC__MUTE",
    0x80 : "KC__VOLUP",
    0x81 : "KC__VOLDOWN",
    0x82 : "KC_LOCKING_CAPS",
    0x83 : "KC_LOCKING_NUM",
    0x84 : "KC_LOCKING_SCROLL",
    0x85 : "KC_KP_COMMA",
    0x86 : "KC_KP_EQUAL_AS400",
    0x87 : "KC_INT1",
    0x88 : "KC_INT2",
    0x89 : "KC_INT3",
    0x8A : "KC_INT4",
    0x8B : "KC_INT5",
    0x8C : "KC_INT6",
    0x8D : "KC_INT7",
    0x8E : "KC_INT8",
    0x8F : "KC_INT9",
    0x90 : "KC_LANG1",
    0x91 : "KC_LANG2",
    0x92 : "KC_LANG3",
    0x93 : "KC_LANG4",
    0x94 : "KC_LANG5",
    0x95 : "KC_LANG6",
    0x96 : "KC_LANG7",
    0x97 : "KC_LANG8",
    0x98 : "KC_LANG9",
    0x99 : "KC_ALT_ERASE",
    0x9A : "KC_SYSREQ",
    0x9B : "KC_CANCEL",
    0x9C : "KC_CLEAR",
    0x9D : "KC_PRIOR",
    0x9E : "KC_RETURN",
    0x9F : "KC_SEPARATOR",
    0xA0 : "KC_OUT",
    0xA1 : "KC_OPER",
    0xA2 : "KC_CLEAR_AGAIN",
    0xA3 : "KC_CRSEL",
    0xA4 : "KC_EXSEL",
}
################################################################################

################################################################################
## base classes byte-streamable / simple representable (jsonifyable) types
# types here:
#   * base scalar (that defaults to a single byte)
#   * homogeneous array
#   * heterogeneous ordered dict
constant0ByteIter = itertools.repeat(0)

class ScalarFieldType(object):
    ID_DEFAULT = "ScalarFieldType"
    BYTE_LEN = 1
    def __init__(self, byteArray=constant0ByteIter, id=None, byteLen=None):
        super(ScalarFieldType, self).__init__()  # python2 compatibility
        self.id = self.ID_DEFAULT if id is None else id
        self.byteLen = self.BYTE_LEN if byteLen is None else byteLen
        self.bytes = byteArray

    def toByteArray(self):
        return self._byteArray

    def fromByteArray(self, byteArray):
        self._byteArray = bytearray()
        for i, byte in zip(range(self.byteLen), iter(byteArray)):
            self._byteArray.append(byte)

    def __str__(self):
        import pprint
        return pprint.pformat(self.simpleRepr)
        
    def toSimpleRepr(self):
        if self.byteLen == 1:
            return self.bytes[0]
        else:
            return list(self.bytes)

    def fromSimpleRepr(self, arg):
        if self.byteLen == 1:
            self.bytes = bytearray([arg])
        else:
            self.bytes = bytearray(arg)
    
    bytes = property(toByteArray, fromByteArray)
    simpleRepr = property(toSimpleRepr, fromSimpleRepr)

class ArrayFieldType(collections.UserList):
    ID_DEFAULT = "ArrayFieldType"
    NUM_ELEM = 2
    ELEM_TYPE = ScalarFieldType
    def __init__(self, byteArray=constant0ByteIter, id=None, numElem=None, elemType=None, ):
        super(ArrayFieldType, self).__init__()  # python2 compatibility
        self.id = self.ID_DEFAULT if id is None else id
        self.numElem = self.NUM_ELEM if numElem is None else numElem
        self.elemType = self.ELEM_TYPE if elemType is None else elemType
        for i in range(self.numElem):
            self.append(self.elemType(iter(byteArray)))
                        
    def toByteArray(self):
        retVal = bytearray()
        for elem in self:
            retVal.extend(elem.bytes)
        return retVal

    def fromByteArray(self, byteArray):
        byteArrayIter = iter(byteArray)
        for elem in self:
            elem.bytes = byteArrayIter

    def __str__(self):
        import pprint
        return pprint.pformat(self.simpleRepr)
        
    def toSimpleRepr(self):
        return [field.simpleRepr for field in self]

    def fromSimpleRepr(self, arg):
        for elem, argElem in zip(self, arg):
            elem.simpleRepr = argElem
    
    bytes = property(toByteArray, fromByteArray)
    simpleRepr = property(toSimpleRepr, fromSimpleRepr)


class CompositeFieldType(collections.OrderedDict):
    ID_DEFAULT = "CompositeFieldType"
    KTM = [("f1", ScalarFieldType), ("f2", ScalarFieldType)]
    def __init__(self, byteArray=constant0ByteIter, id=None, keyToTypeMap=None, ):
        super(CompositeFieldType, self).__init__()
        self.id = self.ID_DEFAULT if id is None else id
        self.keyToTypeMap = self.KTM if keyToTypeMap is None else keyToTypeMap
        for fieldId in self.ktm:
            self[fieldId] = self.ktm[fieldId](iter(byteArray))

    def toByteArray(self):
        retVal = bytearray()
        for fieldId in self:
            retVal.extend(self[fieldId].bytes)
        return retVal

    def fromByteArray(self, byteArray):
        byteArrayIter = iter(byteArray)
        for fieldId in self:
            self[fieldId].bytes = byteArrayIter

    bytes = property(toByteArray, fromByteArray)
################################################################################

if __name__ == '__main__':
    main(sys.argv)

print("start test ")
x = ScalarFieldType()
print(x.simpleRepr)
jsonStr = json.dumps(x.simpleRepr, indent=4)
arr = ArrayFieldType()
arr.bytes = bytearray([10, 42])
print(arr.simpleRepr)
jsonStr = json.dumps(arr.simpleRepr, indent=4)
print(jsonStr)
jsonReload = json.loads(jsonStr, object_pairs_hook=collections.OrderedDict)
arr2 = ArrayFieldType()
arr2.simpleRepr = jsonReload
print(arr2)

print("end test ")

    
