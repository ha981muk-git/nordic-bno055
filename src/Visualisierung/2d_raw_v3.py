#WSN Projekt
#2d vis
#G Georgieva

#untested!!!

import serial
import matplotlib.pyplot as plt

# serial connection
ser = serial.Serial('/dev/ttyACM0', 115200)

max_points = 100  # max number of points on the x-axis

# empty circular buffers to store data
gyro_x = [None] * max_points
gyro_y = [None] * max_points
gyro_z = [None] * max_points
accel_x = [None] * max_points
accel_y = [None] * max_points
accel_z = [None] * max_points
mag_x = [None] * max_points
mag_y = [None] * max_points
mag_z = [None] * max_points

# figure and subplots
fig, axes = plt.subplots(3, 1, figsize=(10, 8))

# set max number of points on the x-axis
axes[0].set_xlim(0, max_points)
axes[1].set_xlim(0, max_points)
axes[2].set_xlim(0, max_points)

# initialize the lines
line_gyro_x, = axes[0].plot([], [], label='X')
line_gyro_y, = axes[0].plot([], [], label='Y')
line_gyro_z, = axes[0].plot([], [], label='Z')
line_accel_x, = axes[1].plot([], [], label='X')
line_accel_y, = axes[1].plot([], [], label='Y')
line_accel_z, = axes[1].plot([], [], label='Z')
line_mag_x, = axes[2].plot([], [], label='X')
line_mag_y, = axes[2].plot([], [], label='Y')
line_mag_z, = axes[2].plot([], [], label='Z')

# titles and labels
axes[0].set_title('Gyroscope Data')
axes[0].set_xlabel('Data Points')
axes[0].set_ylabel('Angular Rate (deg/s)')
axes[1].set_title('Accelerometer Data')
axes[1].set_xlabel('Data Points')
axes[1].set_ylabel('Acceleration (m/s^2)')
axes[2].set_title('Magnetometer Data')
axes[2].set_xlabel('Data Points')
axes[2].set_ylabel('Magnetic Field (µT)')

# loop to continuously plot the data
while True:
    while ser.inWaiting() == 0:
        pass
    # read the serial data
    dataPacket = ser.readline()
    dataPacket = str(dataPacket, 'utf-8')
    data = dataPacket.split(',')

    # ensure correct number of values
    if len(data) == 9:
        # extract the values
        gyro_x.append(float(data[0]))
        gyro_y.append(float(data[1]))
        gyro_z.append(float(data[2]))
        accel_x.append(float(data[3]))
        accel_y.append(float(data[4]))
        accel_z.append(float(data[5]))
        mag_x.append(float(data[6]))
        mag_y.append(float(data[7]))
        mag_z.append(float(data[8]))

        # update circular buffers
        gyro_x.pop(0)
        gyro_y.pop(0)
        gyro_z.pop(0)
        accel_x.pop(0)
        accel_y.pop(0)
        accel_z.pop(0)
        mag_x.pop(0)
        mag_y.pop(0)
        mag_z.pop(0)

        # update plot
        line_gyro_x.set_data(range(len(gyro_x)), gyro_x)
        line_gyro_y.set_data(range(len(gyro_y)), gyro_y)
        line_gyro_z.set_data(range(len(gyro_z)), gyro_z)
        line_accel_x.set_data(range(len(accel_x)), accel_x)
        line_accel_y.set_data(range(len(accel_y)), accel_y)
        line_accel_z.set_data(range(len(accel_z)), accel_z)
        line_mag_x.set_data(range(len(mag_x)), mag_x)
        line_mag_y.set_data(range(len(mag_y)), mag_y)
        line_mag_z.set_data(range(len(mag_z)), mag_z)

        # update plot limits
        axes[0].relim()
        axes[0].autoscale_view()
        axes[1].relim()
        axes[1].autoscale_view()
        axes[2].relim()
        axes[2].autoscale_view()

        # redraw plot
        plt.draw()
        plt.pause(0.01)
