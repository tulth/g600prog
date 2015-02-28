#!/bin/env python
import sys
import itertools
import collections
import json

DEFAULT_IND_STEP = "   "

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


def MOUSE_SCAN_CODE(arg):
    if arg in MOUSE_SCAN_CODES_DICT:
        return MOUSE_SCAN_CODES_DICT[arg]
    else:
        return "UNDEFINED{:02d}".format(arg)

def KB_MODIFIER_BIT_CODE(arg):
    codes = []
    for idx, bit in enumerate(reversed("{:08b}".format(arg))):
        if bit == "1":
            codes.append(KB_MODIFIER_BIT_CODES_DICT[idx])
    retVal = "+".join(codes)
    if retVal == "":
        retVal = "NO_MOD"
    return retVal

def KB_SCAN_CODE(arg):
    if arg in KB_SCAN_CODES_DICT:
        return KB_SCAN_CODES_DICT[arg]
    else:
        return "UNDEFINED{:02d}".format(arg)

constant0ByteIter = itertools.repeat(0)

class ScalarFieldType(object):
    ID_DEFAULT = "ScalarFieldType"
    def __init__(self, id=None, byteArray=constant0ByteIter, indent="", indentStep=DEFAULT_IND_STEP):
        super().__init__()
        if id is None:
            self.id = self.ID_DEFAULT
        else:
            self.id = id
        self.bytes = byteArray
        self.indent=indent

    def toByteArray(self):
        return bytearray([self._b])

    def fromByteArray(self, byteArray):
        b = iter(byteArray).__next__()
        self._b = b

    def renderStr(self):
        return str(self._b)

    def __str__(self):
        return self.indent+self.renderStr()+"\n"

    def toSimpleRepr(self):
#         dictRepr = collections.OrderedDict((("id", self.id), ("body",self._b)))
# #        return json.dumps(dictRepr, indent=4)
#         return dictRepr
        return self._b

    def fromSimpleRepr(self, arg):
        self._b = arg
        
    bytes = property(toByteArray, fromByteArray)

class arrayFieldType(collections.UserList):
    ID_DEFAULT = "arrayFieldType"
    NUM_ELEM = 2
    ELEM_TYPE = ScalarFieldType
    RENDER_FORMAT_STR = "{ind}{index}:\n{fieldStr}"
    def __init__(self, byteArray=constant0ByteIter, indent="", id=None,
                 numElem=None, indentStep=DEFAULT_IND_STEP):
        super().__init__()
        if id is None:
            self.id = self.ID_DEFAULT
        else:
            self.id = id
        if numElem is None:
            self.numElem = self.NUM_ELEM
        else:
            self.numElem = numElem
        self.indent = indent
        self.indentStep = indentStep
        for i in range(self.numElem):
            self.append(self.ELEM_TYPE(indent=self.indent+self.indentStep, indentStep=self.indentStep))
        self.renderFormatStr = self.RENDER_FORMAT_STR
        self.bytes = byteArray

    def toByteArray(self):
        retVal = bytearray()
        for elem in self:
            retVal.extend(elem.bytes)
        return retVal

    def fromByteArray(self, byteArray):
        byteArrayIter = iter(byteArray)
        for elem in self:
            elem.bytes = byteArrayIter

    def renderStr(self):
        retVal = ""
        for index, elem in enumerate(self):
            retVal += self.renderFormatStr.format(ind=self.indent, index=index, fieldStr=elem)
        return retVal

    def __str__(self):
        retVal = self.renderStr()
        return retVal

    def toSimpleRepr(self):
        body = []
        for field in self:
            body.append(field.toSimpleRepr())
        dictRepr = collections.OrderedDict((("id", self.id), ("body",body)))
#        return json.dumps(dictRepr, indent=4)
        return dictRepr

    def fromSimpleRepr(self, arg):
        self.id = arg["id"]
        for elem, argElem in zip(self, arg["body"]):
            elem.fromSimpleRepr(argElem)
    
    bytes = property(toByteArray, fromByteArray)

class compositeFieldType(collections.OrderedDict):
    ID_DEFAULT = "compositeFieldType"
    KTM = [("f1", ScalarFieldType), ("f2", ScalarFieldType)]
    RENDER_FORMAT_STR = "{ind}{fieldId}\n{fieldStr}"
    def __init__(self, byteArray=constant0ByteIter, indent="", id=None,
                 keyToTypeMap=None, indentStep=DEFAULT_IND_STEP):
        super().__init__()
        if id is None:
            self.id = self.ID_DEFAULT
        else:
            self.id = id
        if keyToTypeMap is None:
            self.ktm = collections.OrderedDict(self.KTM)
        else:
            self.ktm = collections.OrderedDict(keyToTypeMap)
        self.indent = indent
        self.indentStep = indentStep
        for fieldId in self.ktm:
            self[fieldId] = self.ktm[fieldId](indent=self.indent+self.indentStep,
                                              indentStep=self.indentStep)
        self.renderFormatStr = self.RENDER_FORMAT_STR
        self.bytes = byteArray

    def toByteArray(self):
        retVal = bytearray()
        for fieldId in self:
            retVal.extend(self[fieldId].bytes)
        return retVal

    def fromByteArray(self, byteArray):
        byteArrayIter = iter(byteArray)
        for fieldId in self:
            self[fieldId].bytes = byteArrayIter

    def renderStr(self):
        retVal = ""
        for fieldId in self:
            retVal += self.renderFormatStr.format(ind=self.indent, fieldId=fieldId, fieldStr=self[fieldId])
        return retVal

    def __str__(self):
        retVal = self.renderStr()
        return retVal

    def toSimpleRepr(self):
        body = collections.OrderedDict()
        for fieldId in self:
            body[fieldId] = self[fieldId].toSimpleRepr()
        dictRepr = collections.OrderedDict((("id", self.id), ("body",body)))
#        return json.dumps(dictRepr, indent=4)
        return dictRepr
    
    def fromSimpleRepr(self, arg):
        self.id = arg["id"]
        for fieldId, argId in zip(self.keys(), arg["body"].keys()):
            self[fieldId].fromSimpleRepr(arg["body"][argId])
            
    bytes = property(toByteArray, fromByteArray)


class G600MouseScanCodeType(ScalarFieldType):
    ID_DEFAULT = "mouseScanCode"
    def renderStr(self):
        return MOUSE_SCAN_CODE(self._b)

class KbModifierBitWiseType(ScalarFieldType):
    ID_DEFAULT = "kbModifier"
    def renderStr(self):
        return KB_MODIFIER_BIT_CODE(self._b)

class KbScanCodeType(ScalarFieldType):
    ID_DEFAULT = "kbScanCode"
    def renderStr(self):
        return KB_SCAN_CODE(self._b)

class G600PollRateType(ScalarFieldType):
    ID_DEFAULT = "pollRate"
    def renderStr(self):
        return str(1000 / (1 + int(self._b)))

class G600DPIType(ScalarFieldType):
    ID_DEFAULT = "dpi"
    def renderStr(self):
        dpiInt=int(self._b)*50
        if dpiInt == 0:
            return "Unused"
        return str(dpiInt)

class G600ModeScalarType(ScalarFieldType):
    ID_DEFAULT = "mode (1, 2, or 3)"
    def renderStr(self):
        if int(self._b) == 0xf3:
            return "mode0"
        elif int(self._b) == 0xf4:
            return "mode1"
        elif int(self._b) == 0xf5:
            return "mode2"
        else:
            return "UNKNOWN"

class G600MouseButtonActionType(compositeFieldType):
    KTM = [(G600MouseScanCodeType.ID_DEFAULT, G600MouseScanCodeType),
           (KbModifierBitWiseType.ID_DEFAULT, KbModifierBitWiseType),
           (KbScanCodeType.ID_DEFAULT, KbScanCodeType),
           ]
#    RENDER_FORMAT_STR = "{fieldStr}"
    def renderStr(self):
        retVal = ""
        valList = []
        for fieldId in self:
            valList.append(str(self[fieldId]).strip())
        retVal = self.indent + " | ".join(valList) + '\n'
        return retVal

class G600LedColorsType(compositeFieldType):
    KTM = [('Red', ScalarFieldType),
           ('Green', ScalarFieldType),
           ('Blue', ScalarFieldType),
           ]
    def renderStr(self):
        retVal = ""
        valList = []
        for fieldId in self:
            valList.append(str(self[fieldId]).strip())
        retVal = self.indent + "RGB: " + "|".join(valList) + '\n'
        return retVal

class G600DPIGroupType(compositeFieldType):
    KTM = [('ShiftDPI', G600DPIType),
           ('DefaultDPIIndex', ScalarFieldType),
           ('DPI1', G600DPIType),
           ('DPI2', G600DPIType),
           ('DPI3', G600DPIType),
           ('DPI4', G600DPIType),
           ]
    RENDER_FORMAT_STR = "{ind}{fieldId}: {fieldStr}\n"
    def renderStr(self):
        retVal = ""
        for fieldId in self:
            retVal += self.renderFormatStr.format(ind=self.indent, fieldId=fieldId,
                                                  fieldStr=str(self[fieldId]).strip())
        return retVal

class G600ButtonMapType(arrayFieldType):
    ID_DEFAULT = "ButtonMap"
    NUM_ELEM = 20
    ELEM_TYPE = G600MouseButtonActionType

class UnknownBytesArray0(arrayFieldType):
    ID_DEFAULT = "Unknown"
    NUM_ELEM = 0x4b-0x44
    ELEM_TYPE = ScalarFieldType
    def renderStr(self):
        return self.indent + str(self.bytes) + '\n'

class UnknownBytesArray1(arrayFieldType):
    ID_DEFAULT = "Unknown"
    NUM_ELEM = 0x5f-0x52
    ELEM_TYPE = ScalarFieldType
    def renderStr(self):
        return self.indent + str(self.bytes) + '\n'

def G600ConfigPageType(byteArray=constant0ByteIter):
    id = "ConfigPage"
    keyToTypeMap = [("ModeNum", G600ModeScalarType),
                    ("LedColors", G600LedColorsType),
                    ("MaybeLighting", UnknownBytesArray0),
                    ("PollRate", G600PollRateType),
                    ("DPI", G600DPIGroupType),
                    ("Unknown1", UnknownBytesArray1),
                    ("buttonMapNormal", G600ButtonMapType),
                    ("buttonMapShift", G600ButtonMapType),
    ]
    return compositeFieldType(byteArray, id=id, keyToTypeMap=keyToTypeMap)

import usb.core
import usb.util

dev = usb.core.find(idVendor=0x046d, idProduct=0xc24a)
interface = 1

if dev.is_kernel_driver_active(interface) is True:
    # tell the kernel to detach
    dev.detach_kernel_driver(interface)
    # claim the device
    usb.util.claim_interface(dev, interface)

for reportId in (0x03f3, 0x03f4, 0x03f5):
    G600_READ_REQTYPE = 0xA1
    G600_READ_REQ = 0x01
    G600_READ_VAL = reportId
    G600_READ_IDX = interface
    G600_READ_LENGTH = 154
    msg = dev.ctrl_transfer(bmRequestType=G600_READ_REQTYPE, # this means control
                            bRequest=G600_READ_REQ,
                            wValue=G600_READ_VAL,
                            wIndex=G600_READ_IDX,
                            data_or_wLength=G600_READ_LENGTH,
                            timeout=None)
    cp = G600ConfigPageType(msg)
    print(cp)

# release the device
usb.util.release_interface(dev, interface)
# reattach the device to the OS kernel
dev.attach_kernel_driver(interface)

print("*"*80)
testPacket = bytearray([
    0xf3, 0x00, 0x00, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x02, 0x00, 0x00, 0x03, 0x00, 0x00, 0x04, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x17, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x05, 0x14, 0x00, 0x00, 0x00, 0x00, 0x1e, 0x00, 0x5b, 0x00, 0x00, 0x5c, 0x00, 0x00, 0x5d, 0x00, 0x00, 0x5e, 0x00, 0x00, 0x5f, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x12, 0x00, 0x00, 0x00, 0x00, 0x08, 0x04, 0x00, 0x00, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ])
cp = G600ConfigPageType(testPacket)
print(cp)
print(isinstance(cp, dict))
jsonStr = json.dumps(cp.toSimpleRepr(), indent=4)
print(jsonStr)
jsonReload = json.loads(jsonStr, object_pairs_hook=collections.OrderedDict)
#print(jsonReload)
cp = G600ConfigPageType()
cp.fromSimpleRepr(jsonReload)
print(cp)
print("*"*80)
