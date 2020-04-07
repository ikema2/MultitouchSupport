#!/usr/bin/env python
import time
import ctypes
import threading
import tkinter
from ctypes.util import find_library

CFArrayRef = ctypes.c_void_p
CFMutableArrayRef = ctypes.c_void_p
CFIndex = ctypes.c_long

MultitouchSupport = ctypes.CDLL("/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport")

CFArrayGetCount = MultitouchSupport.CFArrayGetCount
CFArrayGetCount.argtypes = [CFArrayRef]
CFArrayGetCount.restype = CFIndex

CFArrayGetValueAtIndex = MultitouchSupport.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.argtypes = [CFArrayRef, CFIndex]
CFArrayGetValueAtIndex.restype = ctypes.c_void_p

MTDeviceCreateList = MultitouchSupport.MTDeviceCreateList
MTDeviceCreateList.argtypes = []
MTDeviceCreateList.restype = CFMutableArrayRef

class MTPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float)]

class MTVector(ctypes.Structure):
    _fields_ = [("position", MTPoint),
                ("velocity", MTPoint)]

class MTData(ctypes.Structure):
    _fields_ = [
      ("frame", ctypes.c_int),
      ("timestamp", ctypes.c_double),
      ("identifier", ctypes.c_int),
      ("state", ctypes.c_int),
      ("unknown1", ctypes.c_int),
      ("unknown2", ctypes.c_int),
      ("normalized", MTVector),  # normalized position and vector of the touch (0.0 to 1.0)
      ("size", ctypes.c_float),  # the value in correlation with "shunt current"
      ("unknown3", ctypes.c_int),
      ("angle", ctypes.c_float),
      ("major_axis", ctypes.c_float),
      ("minor_axis", ctypes.c_float),
      ("unknown4", MTVector),
      ("unknown5_1", ctypes.c_int),
      ("unknown5_2", ctypes.c_int),
      ("unknown6", ctypes.c_float),
    ]

MTDataRef = ctypes.POINTER(MTData)

MTContactCallbackFunction = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, MTDataRef,
    ctypes.c_int, ctypes.c_double, ctypes.c_int)

MTDeviceRef = ctypes.c_void_p

MTRegisterContactFrameCallback = MultitouchSupport.MTRegisterContactFrameCallback
MTRegisterContactFrameCallback.argtypes = [MTDeviceRef, MTContactCallbackFunction]
MTRegisterContactFrameCallback.restype = None

MTDeviceStart = MultitouchSupport.MTDeviceStart
MTDeviceStart.argtypes = [MTDeviceRef, ctypes.c_int]
MTDeviceStart.restype = None


@MTContactCallbackFunction
def my_callback(device, data_ptr, n_fingers, timestamp, frame):
    for i in range(n_fingers):
        data = data_ptr[i]
        d = "pos_x=%.2f, pos_y=%.2f, angle=%.2f, major_axis=%.2f, minor_axis=%.2f, size=%.2f" % (data.normalized.position.x,
                                data.normalized.position.y,
                                data.angle,
                                data.major_axis,
                                data.minor_axis,
								data.size)
        print("%d: %s" % (i, d))
    return 0


devices = MultitouchSupport.MTDeviceCreateList()
num_devices = CFArrayGetCount(devices)
for i in range(num_devices):
    device = CFArrayGetValueAtIndex(devices, i)
    MTRegisterContactFrameCallback(device, my_callback)
    MTDeviceStart(device, 0)

while threading.active_count():
    time.sleep(0.125)


