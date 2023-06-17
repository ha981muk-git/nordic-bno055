#WSN Projekt
#2D vis
#G Georgieva

#quicker react

import serial
import matplotlib.pyplot as plt

# serial connection
ser = serial.Serial('/dev/ttyACM0', 115200)

max_points = 100  # max number of points on the x-axis

# empty lists to store data
qw, qx, qy, qz = [], [], [], []

# create figure and subplot
fig, ax = plt.subplots(figsize=(10, 6))

# initialize the lines
line_qw, = ax.plot([], [], label='w')
line_qx, = ax.plot([], [], label='x')
line_qy, = ax.plot([], [], label='y')
line_qz, = ax.plot([], [], label='z')

# max number of data points
ax.set_xlim(0, max_points)

# titles and labels
ax.set_title('Quaternion Data')
ax.set_xlabel('Data points')
ax.set_ylabel('Value')

# legend
ax.legend(loc="upper left")

# text annotations for variable values
text_qw = ax.text(0.9, 0.95, '', transform=ax.transAxes, ha='left', va='top')
text_qx = ax.text(0.9, 0.90, '', transform=ax.transAxes, ha='left', va='top')
text_qy = ax.text(0.9, 0.85, '', transform=ax.transAxes, ha='left', va='top')
text_qz = ax.text(0.9, 0.80, '', transform=ax.transAxes, ha='left', va='top')

# blitting on
fig.canvas.draw()
background = fig.canvas.copy_from_bbox(ax.bbox)

# loop to continuously plot the data
while True:
    while ser.inWaiting() == 0:
        pass

    # read serial data
    dataPacket = ser.readline()
    dataPacket = str(dataPacket, 'utf-8')
    splitPacket = dataPacket.split(',')
    scale = (1.0 / (1 << 14))

    if len(splitPacket) == 4:
        # extract quaternion values
        qw.append(float(splitPacket[0]) * scale)
        qx.append(float(splitPacket[1]) * scale)
        qy.append(float(splitPacket[2]) * scale)
        qz.append(float(splitPacket[3]) * scale)

        # limit the length of the lists
        qw = qw[-max_points:]
        qx = qx[-max_points:]
        qy = qy[-max_points:]
        qz = qz[-max_points:]

        # update lines with new data
        line_qw.set_data(range(len(qw)), qw)
        line_qx.set_data(range(len(qx)), qx)
        line_qy.set_data(range(len(qy)), qy)
        line_qz.set_data(range(len(qz)), qz)

        # update text annotations
        text_qw.set_text(f'qw: {qw[-1]:.3f}')
        text_qx.set_text(f'qx: {qx[-1]:.3f}')
        text_qy.set_text(f'qy: {qy[-1]:.3f}')
        text_qz.set_text(f'qz: {qz[-1]:.3f}')

        # update y-axis limits based on the data range
        y_min = min(min(qw), min(qx), min(qy), min(qz))
        y_max = max(max(qw), max(qx), max(qy), max(qz))
        ax.set_ylim(y_min, y_max)

        # restore background and redraw lines and text
        fig.canvas.restore_region(background)
        ax.draw_artist(line_qw)
        ax.draw_artist(line_qx)
        ax.draw_artist(line_qy)
        ax.draw_artist(line_qz)
        ax.draw_artist(text_qw)
        ax.draw_artist(text_qx)
        ax.draw_artist(text_qy)
        ax.draw_artist(text_qz)

        # update plot
        fig.canvas.blit(ax.bbox)

        # pause to allow the plot to be shown
        plt.pause(0.001)
