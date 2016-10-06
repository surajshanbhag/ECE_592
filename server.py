#!/usr/bin/python
# first of all import the socket library
import random
import Adafruit_BBIO.ADC as ADC
import socket
import subprocess
import time
# next create a socket object
s = socket.socket()
print "Socket successfully created"

# reserve a port on your computer in our
# case it is 12345 but it can be anything
port = 12345

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))
print "socket binded to %s" %(port)

# put the socket into listening mode
s.listen(5)
print "socket is listening"

# a forever loop until we interrupt it or
# an error occurs
count=0
c, addr = s.accept()
print 'Got connection from', addr

#sensor pin connection
pin_accel_x=0;
pin_accel_y=0;
pin_accel_z=0;
pin_accel_linear=0;
pin_gyro_yaw=0;
pin_gyro_roll=0;
pin_gyro_pitch=0;
pin_pulse_raw="P9_40";
pin_emg_raw=0;
pin_temp_raw=0;

#sensor data
accel_x=0;
accel_y=0;
accel_z=0;
accel_linear=0;
gyro_yaw=0;
gyro_roll=0;
gyro_pitch=0;
pulse_raw=0;
emg_raw=0;
temp_raw=0;

# Select data to be streamed
ON_accel_x=1;
ON_accel_y=1;
ON_accel_z=1;
ON_accel_linear=0;
ON_gyro_yaw=0;
ON_gyro_roll=0;
ON_gyro_pitch=0;
ON_pulse_raw=1;
ON_emg_raw=1;
ON_temp_raw=1;

ADC.setup()

while True:
    start = time.time()
    # Establish connection with client.
# send a thank you message to the client.
    p = subprocess.Popen("./cpu_temp", stdout=subprocess.PIPE, shell=True)
    (temp, err)=p.communicate()
    p.wait()
    #c.send(temp.strip()+"$")
    accel_x=random.uniform(-20,20);
    accel_y=random.uniform(-20,20);
    accel_z=random.uniform(-20,20);
    accel_linear=random.uniform(1.5,1.9);
    gyro_yaw=random.uniform(1.5,1.9);
    gyro_roll=random.uniform(1.5,1.9);
    gyro_pitch=random.uniform(1.5,1.9);
    #pulse_raw=random.uniform(-100,100);
    pulse_raw=ADC.read(pin_pulse_raw)
    emg_raw=random.uniform(1.5,1.9);
    temp_raw=random.uniform(1.5,1.9);

    if ON_temp_raw == 1:
        output=temp.strip()+";";

    if ON_pulse_raw == 1:
        output+=str(pulse_raw)+";";

    if ON_emg_raw == 1:
        output+=str(emg_raw)+";";

    if ON_accel_linear == 1:
        output+=str(accel_linear)+";";

    if ON_accel_x == 1:
        output+=str(accel_x)+";";

    if ON_accel_y == 1:
        output+=str(accel_y)+";";

    if ON_accel_z == 1:
        output+=str(accel_z)+";";

    if ON_gyro_yaw == 1:
        output+=str(gyro_yaw)+";";

    if ON_gyro_roll == 1:
        output+=str(gyro_roll)+";";

    if ON_gyro_pitch == 1:
        output+=str(gyro_pitch);

    #print(output+"$\n");
    end = time.time()
    c.send(output+"$");
    #print(end - start)
    count=count+1
    print(".")
    print(str(len(output))+"\n");
    #time.sleep(1);
# Close the connection with the client
c.close()
