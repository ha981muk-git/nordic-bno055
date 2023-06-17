# 3D Visualizierung
# WSN Projekt
# Georgieva, Gergana
# 3D board model
# works!!!

from vpython import *
from time import *
import numpy as np
import math
import serial

sensorData = serial.Serial('/dev/ttyACM1', 115200)
sleep(1)

#toRad = 2*np.pi/360
#toDeg = 1/toRad
scale = (1.0 / (1 << 14))


scene.range = 12
scene.forward = vector(6, -1, 1)
scene.width = 800
scene.height = 600
scene.background = color.white

pos_nrfboard = vector(0, 0, 0)
Xarrow_nrf = arrow(pos=pos_nrfboard, length=3, shaftwidth=.1, color=color.red, axis=vector(1,0,0), opacity=.5)
Yarrow_nrf = arrow(pos=pos_nrfboard, length=3, shaftwidth=.1, color=color.green, axis=vector(0,1,0), opacity=.5)
Zarrow_nrf = arrow(pos=pos_nrfboard, length=3, shaftwidth=.1, color=color.blue, axis=vector(0,0,1), opacity=.5)

front_arrow_nrf = arrow(pos=pos_nrfboard, length=1, shaftwidth=.1, color=color.yellow, axis=vector(1,0,0), opacity=.5)
up_arrow_nrf = arrow(pos=pos_nrfboard, length=1, shaftwidth=.1, color=color.magenta, axis=vector(0,1,0), opacity=.5)
side_arrow_nrf = arrow(pos=pos_nrfboard, length=1, shaftwidth=.1, color=color.cyan, axis=vector(0,0,1), opacity=.5)


connections_color = vec(0.2, 0.2, 0.2) #black-ish

bno055 = box(length=0.5, width=0.38, height=0.04, opacity=.75, pos=vec(0, -0.065, 0), color=connections_color)
bno055PCB = box(length=2, width=2.7, height=.13, opacity=.9, pos=vec(0, -0.13, 0), color=vec(0, 0.54, 0.69))
bno055con1 = box(length=0.25, width=1.2, height=1.03, opacity=.75, pos=vec(-0.85, -0.7025, 0), color=connections_color)
bno055con2 = box(length=0.25, width=1.6, height=1.03, opacity=.75, pos=vec(0.85, -0.7025, 0), color=connections_color)

bno055board = compound([bno055PCB,
                        bno055,
                        bno055con1,
                        bno055con2], pos=vec(0,0,0), origin=vec(0,0,0))

nordic = box(length=6.4, width=13.6, height=.13, opacity=.75, pos=vec(3.2, 0, 6.8), color=vec(0.17, 0.296, 0.533))
nrf = box(length=0.7, width=0.7, height=0.04, opacity=.75, pos=vec(1.9, 0.085, 2), color=connections_color)
nordiccon1 = box(length=0.25, width=2.1, height=0.7, opacity=.75, pos=vec(0.65, 0.35, 7.85), color=connections_color)
nordiccon2 = box(length=0.25, width=2.1, height=0.7, opacity=.75, pos=vec(0.65, 0.35, 5.5), color=connections_color)
nordiccon3 = box(length=0.25, width=1.5, height=0.7, opacity=.75, pos=vec(5.54, 0.35, 7.9), color=connections_color)
nordiccon4 = box(length=2.3, width=0.5, height=0.7, opacity=.75, pos=vec(1.9, 0.35, 4.0), color=connections_color)

nordicboard = compound([nordic,
                        nrf,
                        nordiccon1,
                        nordiccon2,
                        nordiccon3,
                        nordiccon4], pos=vec(-3.2, -2.55, -10), origin=vec(0, 0, 0))


color_bridge = vec(0.21,0.748,0.042) #green

bridgepcb1 = box(length=5.3, width=1.8, height=0.13, opacity=.75, pos=vec(2.65, 0, 0.9), color=color_bridge)
bridgepcb2 = box(length=1.5, width=0.9, height=0.13, opacity=.75, pos=vec(0.75, 0, 2.25), color=color_bridge)
bridgepcb3 = box(length=0.9, width=0.3, height=0.13, opacity=.75, pos=vec(4.85, 0, -0.15), color=color_bridge)
bridgei2ccon = box(length=0.25, width=2.6, height=1.2, opacity=.75, pos=vec(0.1, -0.685, 1.3), color=connections_color)
bridgepwcon = box(length=0.25, width=2.1, height=1.2, opacity=.75, pos=vec(5, -0.685, 0.78), color=connections_color)

bridge = compound([bridgepcb1,
                   bridgepcb2,
                   bridgepcb3,
                   bridgei2ccon,
                   bridgepwcon], pos=vec(-2.65, -1.275, -0.9), origin=vec(0, 0, 0))

Obj = compound([bno055board,
                nordicboard,
                bridge], pos=pos_nrfboard, origin=vector(0, 0, 0))


while True:
    while sensorData.inWaiting() == 0:
        pass
    dataPacket = sensorData.readline()
    dataPacket = str(dataPacket, 'utf-8')
    splitPacket = dataPacket.split(',')
    moduleid = splitPacket[0]
    qw = float(splitPacket[1]) * scale
    qx = float(splitPacket[2]) * scale
    qy = float(splitPacket[3]) * scale
    qz = float(splitPacket[4]) * scale

    #print("qw: ", qw, " qx: ", qx, " qy: ", qy, " qz: ", qz)

    roll = 0
    yaw = 0
    pitch = 0

    unitLength = qw**2 + qx**2 + qy**2 + qz**2
    abcd = qw*qx + qy*qz #roll part

    if unitLength != 0:
        if abcd > (0.4995)*unitLength:
            yaw = 2*atan2(qy, qw)
            pitch = np.pi/2
            roll = 0
            print("Singularity at north pole", "pitch ", pitch, "yaw ", yaw)
        elif abcd < (-0.4995)*unitLength:
            yaw = -2 * atan2(qy, qw)
            pitch = -np.pi / 2
            roll = 0
            print("Singularity at south pole", "pitch ", pitch, "yaw ", yaw)
        else:
            #pitch and roll partially switched
            #no full rotation on them (go throught the alternative state at 90 deg)
        #roll = atan2(2 * (qw * qy - qx * qz), 1 - 2 * (qx ** 2 + qy ** 2))
        #pitch = asin(2 * (qw * qx + qy * qz)/unitLength)
        #yaw = -atan2(2 * (qw * qz - qx * qy), 1 - 2 * (qy ** 2 + qz ** 2))
            # for yaw both + and - work????

            adbc = qw*qz - qx*qy
            acbd = qw*qy - qx*qz
            roll = atan2(2*acbd, 1 - 2*(qx**2 + qy**2))
            pitch = asin(2*abcd/unitLength)
            yaw = -atan2(2*adbc, 1 - 2*(qz**2 + qx**2))

        rate(20)
        k = vector(cos(yaw) * cos(pitch), sin(pitch), sin(yaw) * cos(pitch))
        y = vector(0, 1, 0)
        s = cross(k, y)
        v = cross(s, k)
        vrot = v * cos(roll) + cross(k, v) * sin(roll)

        front_arrow_nrf.axis = k
        side_arrow_nrf.axis = cross(k, vrot)
        up_arrow_nrf.axis = vrot
        Obj.axis = k
        Obj.up = vrot

       # print("roll: ", roll, "pitch: ", pitch, "yaw: ", yaw)
