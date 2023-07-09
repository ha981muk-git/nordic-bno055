import math
import sys
import time as time_  # make sure we don't override time
import numpy as np
import serial
from vpython import *

# from src.euler_angles import Quaternion, EulerAngles, to_euler_angles, print_position
print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/Users/harsh/PycharmProjects/nordic-bno055'])

toRad = 2 * np.pi / 360
toDeg = 1 / toRad
scale = (1.0 / (1 << 14))

scene.range = 12
scene.forward = vector(-1, -1, -1)

scene.width = 1980
scene.height = 980

scene.background = color.white

posfhmodul = vector(0, 0, 0)

xarrowfh = arrow(pos=posfhmodul, length=3, shaftwidth=.1, color=color.red, axis=vector(1, 0, 0), opacity=.5)
yarrowfh = arrow(pos=posfhmodul, length=3, shaftwidth=.1, color=color.green, axis=vector(0, 1, 0), opacity=.5)
zarrowfh = arrow(pos=posfhmodul, length=3, shaftwidth=.1, color=color.blue, axis=vector(0, 0, 1), opacity=.5)

frontArrowfh = arrow(pos=posfhmodul, length=4, shaftwidth=.1, color=color.purple, axis=vector(1, 0, 0), opacity=.5)
upArrowfh = arrow(pos=posfhmodul, length=1, shaftwidth=.1, color=color.magenta, axis=vector(0, 1, 0), opacity=.5)
sideArrowfh = arrow(pos=posfhmodul, length=1, shaftwidth=.1, color=color.orange, axis=vector(0, 0, 1), opacity=.5)

bno055 = box(length=0.5, width=0.38, height=0.04, opacity=.75, pos=vec(0, -0.065, 0), color=vec(0.2, 0.2, 0.2))
bno055PCB = box(length=2, width=2.7, height=.13, opacity=.75, pos=vec(0, -0.13, 0.0), color=vec(0, 0.54, 0.69))
bno055con1 = box(length=0.25, width=1.2, height=1.03, opacity=.75, pos=vec(-0.85, -0.7025, 0), color=vec(0.2, 0.2, 0.2))
bno055con2 = box(length=0.25, width=1.6, height=1.03, opacity=.75, pos=vec(0.85, -0.7025, 0), color=vec(0.2, 0.2, 0.2))

bno055board = compound([bno055PCB, bno055, bno055con1, bno055con2], pos=vec(0, 0, 0), origin=vec(0, 0, 0))

nordicdkpcb = box(length=6.4, width=13.6, height=.13, opacity=.75, pos=vec(3.2, 0, 6.8), color=vec(0, 0.8, 0.5))
nrf52840 = box(length=0.7, width=0.7, height=0.04, opacity=.75, pos=vec(1.9, 0.085, 2), color=vec(0.2, 0.2, 0.2))

nordicdkcon1 = box(length=0.25, width=2.1, height=0.7, opacity=.75, pos=vec(0.65, 0.35, 7.85), color=vec(0.2, 0.2, 0.2))
nordicdkcon2 = box(length=0.25, width=2.1, height=0.7, opacity=.75, pos=vec(0.65, 0.35, 5.5), color=vec(0.2, 0.2, 0.2))
nordicdkcon3 = box(length=0.25, width=1.5, height=0.7, opacity=.75, pos=vec(5.54, 0.35, 7.9), color=vec(0.2, 0.2, 0.2))
nordicdkcon4 = box(length=2.3, width=0.5, height=0.7, opacity=.75, pos=vec(1.9, 0.35, 4.0), color=vec(0.2, 0.2, 0.2))

nordicboard = compound([nordicdkpcb, nrf52840, nordicdkcon1, nordicdkcon2, nordicdkcon3, nordicdkcon4],
                       pos=vec(-3.2, -2.55, -10), origin=vec(0, 0, 0))

bridgepcb1 = box(length=5.3, width=1.8, height=.13, opacity=.75, pos=vec(2.65, 0, 0.9), color=vec(1, 0, 0))
bridgepcb2 = box(length=1.5, width=0.9, height=.13, opacity=.75, pos=vec(0.75, 0, 2.25), color=vec(1, 0, 0))
bridgepcb3 = box(length=0.9, width=0.3, height=.13, opacity=.75, pos=vec(4.85, 0, -0.15), color=vec(1, 0, 0))
bridgei2ccon = box(length=0.25, width=2.6, height=1.2, opacity=.75, pos=vec(0.1, -0.685, 1.3), color=vec(0.2, 0.2, 0.2))
bridgepwcon = box(length=0.25, width=2.1, height=1.2, opacity=.75, pos=vec(5, -0.685, 0.78), color=vec(0.2, 0.2, 0.2))

bridge = compound([bridgepcb1, bridgepcb2, bridgepcb3, bridgei2ccon, bridgepwcon], pos=vec(-2.65, -1.275, -0.9),
                  origin=vec(0, 0, 0))

fhObj = compound([bno055board, nordicboard, bridge], pos=posfhmodul, origin=vector(0, 0, 0))


def rotatefhObj(roll, pitch, yaw, flag):

    k = vector(cos(yaw) * cos(pitch), sin(pitch), sin(yaw) * cos(pitch))
    y = vector(0, 1, 0)
    s = cross(k, y)
    v = cross(s, k)

    vrot = v * cos(roll) + cross(k, v) * sin(roll)

    frontArrowfh.axis = k
    sideArrowfh.axis = cross(k, vrot)
    upArrowfh.axis = vrot

    fhObj.axis = k * flag
    fhObj.up = vrot
    sideArrowfh.length, frontArrowfh.length, upArrowfh.length = 4, 4, 4
