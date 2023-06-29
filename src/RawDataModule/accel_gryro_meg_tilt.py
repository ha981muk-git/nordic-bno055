# berichtigte Version, Gimbal lock wird vermieden
# alte Version ist auskommentiert
from vpython import *
from time import *
import numpy as np
import math
import serial
import sys

# from src.euler_angles import Quaternion, EulerAngles, to_euler_angles, print_position

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/Users/harsh/PycharmProjects/3d-modelling'])

arduinoData = serial.Serial('/dev/tty.usbmodem0006839967901', 115200)
sleep(1)

rollFold = 0
pitchFold = 0
yawFold = 0

toRad = 2 * np.pi / 360
toDeg = 1 / toRad
scale = (1.0 / (1 << 14))

scene.range = 12
scene.forward = vector(6, -1, 1)
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

bno055board = compound([bno055PCB,
                        bno055,
                        bno055con1,
                        bno055con2
                        ],
                       pos=vec(0, 0, 0), origin=vec(0, 0, 0))

nordicdkpcb = box(length=6.4, width=13.6, height=.13, opacity=.75, pos=vec(3.2, 0, 6.8), color=vec(0, 0.8, 0.5))
nrf52840 = box(length=0.7, width=0.7, height=0.04, opacity=.75, pos=vec(1.9, 0.085, 2), color=vec(0.2, 0.2, 0.2))

nordicdkcon1 = box(length=0.25, width=2.1, height=0.7, opacity=.75, pos=vec(0.65, 0.35, 7.85), color=vec(0.2, 0.2, 0.2))
nordicdkcon2 = box(length=0.25, width=2.1, height=0.7, opacity=.75, pos=vec(0.65, 0.35, 5.5), color=vec(0.2, 0.2, 0.2))
nordicdkcon3 = box(length=0.25, width=1.5, height=0.7, opacity=.75, pos=vec(5.54, 0.35, 7.9), color=vec(0.2, 0.2, 0.2))
nordicdkcon4 = box(length=2.3, width=0.5, height=0.7, opacity=.75, pos=vec(1.9, 0.35, 4.0), color=vec(0.2, 0.2, 0.2))

nordicboard = compound([nordicdkpcb,
                        nrf52840,
                        nordicdkcon1,
                        nordicdkcon2,
                        nordicdkcon3,
                        nordicdkcon4
                        ],
                       pos=vec(-3.2, -2.55, -10), origin=vec(0, 0, 0))

bridgepcb1 = box(length=5.3, width=1.8, height=.13, opacity=.75, pos=vec(2.65, 0, 0.9), color=vec(1, 0, 0))
bridgepcb2 = box(length=1.5, width=0.9, height=.13, opacity=.75, pos=vec(0.75, 0, 2.25), color=vec(1, 0, 0))
bridgepcb3 = box(length=0.9, width=0.3, height=.13, opacity=.75, pos=vec(4.85, 0, -0.15), color=vec(1, 0, 0))
bridgei2ccon = box(length=0.25, width=2.6, height=1.2, opacity=.75, pos=vec(0.1, -0.685, 1.3), color=vec(0.2, 0.2, 0.2))
bridgepwcon = box(length=0.25, width=2.1, height=1.2, opacity=.75, pos=vec(5, -0.685, 0.78), color=vec(0.2, 0.2, 0.2))
bridge = compound([bridgepcb1,
                   bridgepcb2,
                   bridgepcb3,
                   bridgei2ccon,
                   bridgepwcon
                   ],
                  pos=vec(-2.65, -1.275, -0.9), origin=vec(0, 0, 0))

fhObj = compound([bno055board,
                  nordicboard,
                  bridge],
                # pos=posfhmodul, origin=vector(0, 0, 0)
                 )


data_w = 0
data_x = 0
data_y = 0
data_z = 0
# com_q = data_w & data_x & data_y & data_z
# print(com_q)

fhObj.velocity = vector(0,0,0)

thetaG = 0
phiG = 0

import time as time_ #make sure we don't override time
def millis():
    return int(round(time_.time() * 1000))

millisOld = millis()

while True:
    while arduinoData.inWaiting() == 0:
        pass
    dataPacket = arduinoData.readline()
    dataPacket = str(dataPacket, 'utf-8')
    print(dataPacket)
    splitPacket = dataPacket.split(',')
    qw = float(splitPacket[0]) * scale
    qx = float(splitPacket[1]) * scale
    qy = float(splitPacket[2]) * scale
    qz = float(splitPacket[3]) * scale
    ax = float(splitPacket[4]) * scale
    ay = float(splitPacket[5]) * scale
    az = float(splitPacket[6]) * scale
    gx = float(splitPacket[7]) * scale
    gy = float(splitPacket[8]) * scale
    gz = float(splitPacket[9]) * scale
    mx = float(splitPacket[10]) * scale
    my = float(splitPacket[11]) * scale
    mz = float(splitPacket[12]) * scale

    # DETERMINE TILT FROM 3-AXIS ACCELEROMETER
    theta = -atan2(ax / 9.8, az / 9.8) / 2 / 3.141592654 * 360
    phi = -atan2(ay / 9.8, az / 9.8) / 2 / 3.141592654 * 360
    # theta is angle with plain surface and phi is roll or
    print("theta = ", theta, " phi = ", phi)

    #Gyro measures the angular velocity of hardware with surface and roll
    dt = (millis() - millisOld) / 1000.
    millisOld = millis()

    thetaG = thetaG + gy * dt # v = u + at
    phiG = phiG - gx * dt
    # final angle of device with thetaG and phiG
    print("thetaG = ", thetaG, " phiG = ", phiG)

    # magnotometer measure compensated compass direction
    phiRad=phiG/360*(2*3.14)
    thetaRad=thetaG/360*(2*3.14)

    Xm=mx*cos(thetaRad)-my*sin(phiRad)*sin(thetaRad)+mz*cos(phiRad)*sin(thetaRad)
    Ym=my*cos(phiRad)+mz*sin(phiRad)
    #  Kompassrichtung zu bestimmen
    psi = atan2(Ym, Xm) / (2 * 3.14) * 360

    print("phiM = ", psi)

   # qm = float(splitPacket[4]) * scale

    # print("qw", qw, "qx", qx, "qy", qy, "qz", qz)
    sqw = qw * qw
    sqx = qx * qx
    sqy = qy * qy
    sqz = qz * qz
    test = qx * qy + qz * qw

    roll = 0
    yaw = 0
    pitch = 0
    # acceleration
    #if not (data_ax == 0 and data_ay == 0 and data_az == 0):
    acc = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
    print("acc = ",acc)

    # pitch = atan2 (2*qy*qw-2*qx*qz, 1 - 2*qy**2 - 2*qz**2)
    # yaw asin(2*qx*qy + 2*qz*qw)
    # roll = atan2 (2*qx*qw-2*qy *qz, 1 - 2*qx**2 - 2*qz**2)

    unitLength = qw ** 2 + qx ** 2 + qy ** 2 + qz ** 2
    abcd = qw * qx + qy * qz

    if unitLength != 0:
        if abcd > 0.4995 * unitLength:
            yaw = 2 * atan2(qy, qw)
            pitch = np.pi / 2
            roll = 0
            print("singularity at north pole", "pitch", pitch, "yaw", yaw)

        elif abcd < (-0.4995) * unitLength:
            yaw = -2 * atan2(qy, qw)
            pitch = np.pi / 2
            roll = 0
            print("singularity at south pole", "pitch", pitch, "yaw", yaw)

        else:
            adbc = qw * qz - qx * qy
            acbd = qw * qy - qx * qz
            yaw = -atan2(2 * adbc, 1 - 2 * (qz ** 2 + qx ** 2))
            pitch = asin(2 * abcd / unitLength)
            roll = atan2(2 * acbd, 1 - 2 * (qy ** 2 + qx ** 2))

    rollFnew = 0.90 * rollFold + 0.1 * roll
    yawFnew = 0.90 * yawFold + 0.1 * yaw
    pitchFnew = 0.90 * pitchFold + 0.1 * pitch

    k = vector(cos(yawFnew) * cos(pitchFnew), sin(pitchFnew), sin(yawFnew) * cos(pitchFnew))
    y = vector(0, 1, 0)
    s = cross(k, y)
    v = cross(s, k)

    vrot = v * cos(rollFnew) + cross(k, v) * sin(rollFnew) #+ fhObj.velocity

    frontArrowfh.axis = k
    sideArrowfh.axis = cross(k, vrot)
    upArrowfh.axis = vrot

    fhObj.axis = k
    fhObj.up = vrot

    sideArrowfh.length = 4
    frontArrowfh.length = 4
    upArrowfh.length = 4

    rollFold = roll
    pitchFold = pitch
    yawFold = yaw

    if not (data_x == 0 and data_y == 0 and data_z == 0):
        fhObj.velocity = vector(qx - data_x, qy - data_y, qz - data_z) * 10

   # fhObj.pos = fhObj.pos + fhObj.velocity

    #fhObj.pos = vector(qx, qy, qz)



    data_w = qw
    data_x = qx
    data_y = qy
    data_z = qz


