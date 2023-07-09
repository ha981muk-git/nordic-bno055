from nordicBoard3d import *

arduinoData = serial.Serial('/dev/tty.usbmodem0006839967901', 115200)
sleep(1)

thetaG, phiG = 0, 0
theta, phi = 0, 0
thetaFold, phiFold = 0, 0

def millis():
    return int(round(time_.time() * 1000))


millisOld = millis()

while True:
    while arduinoData.inWaiting() == 0:
        pass
    dataPacket = arduinoData.readline()
    try:
        dataPacket = str(dataPacket, 'utf-8')
    except UnicodeDecodeError:
        pass
    splitPacket = dataPacket.split(',')

    if len(dataPacket.split(',')) != 13:
        pass
    # just removed quaternions because we were working with acc,gyro,meg not with quaternions
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
    thetaA = -atan2(ax / 9.8, az / 9.8) / 2 / 3.141592654 * 360
    phiA = -atan2(ay / 9.8, az / 9.8) / 2 / 3.141592654 * 360
    # theta is angle with plain surface (pitch) and phi(roll) and data is being filtered here
    phiAFnew = 0.95 * phiFold + 0.05 * phiA
    thetaAFnew = 0.95 * thetaFold + 0.05 * thetaA

    # Gyro measures the angular velocity of hardware with surface and roll
    dt = (millis() - millisOld) / 1000.
    millisOld = millis()

    theta = (theta + gy * dt) * 0.95 + thetaA * 0.05  # v = u + at
    phi = (phi - gx * dt) * 0.95 + phiA * 0.05

    thetaG = thetaG + gy * dt  # v = u + at
    phiG = phi - gx * dt

    # final angle of device with thetaG and phiG
    # print("thetaG = ", thetaG, " phiG = ", phiG)

    # magnotometer measure compensated compass direction
    phiRad = phiG / 360 * (2 * 3.14)
    thetaRad = thetaG / 360 * (2 * 3.14)

    Xm = mx * cos(thetaRad) - my * sin(phiRad) * sin(thetaRad) + mz * cos(phiRad) * sin(thetaRad)
    Ym = my * cos(phiRad) + mz * sin(phiRad)

    #  Kompassrichtung zu bestimmen # psi is yaw
    psi = atan2(Ym, Xm) / (2 * 3.14) * 360
    # print("phiM = ", psi)
    # print("t= ", thetaA, "pi= ", phiA, "psi= ", psi)

    # acceleration
    acc = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
    # print("acc = ", acc)

    rollFnew = math.radians(theta)
    yawFnew = math.radians(psi)
    pitchFnew = math.radians(phi)
    flag = -1
    rotatefhObj(rollFnew, pitchFnew, yawFnew, flag)

    thetaFold, phiFold = theta, phi
