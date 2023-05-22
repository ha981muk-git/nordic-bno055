import time         # Library for the delay function, time() to create timestamps
import serial       # Library for the Serial functions to establish connections with the port, pip install pyserial
import keyboard     # Library to create own defined keyfunctions, pip install keyboard

#from datetime import datetime //timer dependent on time of day
#timestamp = datetime.now().strftime('%M:%S.%f') # Format timestamp as mm:ss:ms

import module_db    # Include database File

# Variables
stop_program = False        # Variable to stop Program with a key
start_time = time.time()    # Decleration of Timer (Start)
packet_count = 0
module_id = 1               # The ID of the module from the Modules table


# Help Function to stop the loop and close the connection with the port and DB
def stop_program_callback(e):
    global stop_program
    stop_program = True
    module_db.con.close()
    nrfData.close()

keyboard.on_press_key("esc", stop_program_callback)


# Crating an Object which is linked to the used port
nrfData=serial.Serial('com3', 115200)
time.sleep(1)


# Catching data from the port and print it in python out
while not stop_program:

    # Wait until there is data waiting in the serial buffer
    while (nrfData.inWaiting()==0):
        pass

    # Read data out of the buffer until a carraige return / new line is found
    dataPacket = nrfData.readline()
    # Setting String value of dataPacket to utf-8, to not read undesired characters
    dataPacket=str(dataPacket,'utf-8')
    #print(dataPacket)

    # Splitting dataPacket (/ single String) by a delimeter (here ",")
    # and saving numbers in an Array
    splitPacket=dataPacket.split(",")
    #print (splitPacket)
    x=float(splitPacket[0])             # Note: working later with float numbers
    y=float(splitPacket[1])
    z=float(splitPacket[2])
    #print ("X =",x,"Y =",y,"Z =",z)

    # Calcuating time since new catched data
    current_time = time.time()
    elapsed_time = current_time - start_time
    timestamp = elapsed_time

    # Make sure how fast the write operation is
    data_rate = packet_count / elapsed_time
    packet_count += 1
    print(data_rate)

    # Insertion in the DB
    module_db.insert_data(timestamp, x, y, z, module_id)
    module_db.insert_module(module_id)



