from nordicBoard3d import *

nordicBoard = '/dev/tty.usbmodem0006838612801'

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

    # print("qw", qw, "qx", qx, "qy", qy, "qz", qz)
    sqw = qw * qw
    sqx = qx * qx
    sqy = qy * qy
    sqz = qz * qz
    test = qx * qy + qz * qw

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
    flag = 1
    rotatefhObj(rollFnew, pitchFnew, yawFnew, flag)

    rollFold, pitchFold, yawFold = rollFnew, pitchFnew, yawFnew
