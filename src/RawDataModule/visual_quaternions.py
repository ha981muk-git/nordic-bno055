from nordicBoard3d import *

arduinoData = serial.Serial(nordicBoard, 115200)
sleep(1)

roll, pitch, yaw = 0, 0, 0

rollFold, pitchFold, yawFold = 0, 0, 0

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

    splitPacket = dataPacket.split(',')
    qw = float(splitPacket[0]) * scale
    qx = float(splitPacket[1]) * scale
    qy = float(splitPacket[2]) * scale
    qz = float(splitPacket[3]) * scale

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

    rollFnew = 0.95 * rollFold + 0.05 * roll
    yawFnew = 0.95 * yawFold + 0.05 * yaw
    pitchFnew = 0.95 * pitchFold + 0.05 * pitch
    #print(roll * toDeg,pitch *toDeg,yaw*toDeg)
    pitchFnew = -pitchFnew

    k = vector(cos(yawFnew) * cos(pitchFnew), sin(pitchFnew), sin(yawFnew) * cos(pitchFnew))
    y = vector(0, 1, 0)
    s = cross(k, y)
    v = cross(s, k)

    vrot = v * cos(rollFnew) + cross(k, v) * -sin(rollFnew)

    frontArrowfh.axis = k
    sideArrowfh.axis = cross(k, vrot)
    upArrowfh.axis = vrot

    fhObj.axis = -k
    fhObj.up = vrot

    sideArrowfh.length = 4
    frontArrowfh.length = 4
    upArrowfh.length = 4

    #rotatefhObj(rollFnew, pitchFnew, yawFnew, flag)

    rollFold, pitchFold, yawFold = roll, pitch, yaw
