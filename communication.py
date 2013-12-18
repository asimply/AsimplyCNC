#!/usr/bin/env python3
# encoding: utf-8

import serial
import time
import os
import threading

class order (object):
    __init__(self, incrX, incrY, incrZ):
        self.incrX = incrX
        self.incrY = incrY
        self.incrZ = incrZ
        
    __str__(self):
        return ("M1X" + str(self.incrX) + "Y" + str(self.incrY) + "Z" + str(self.incrZ) + "\n")
