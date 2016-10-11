#!/usr/bin/python
# first of all import the socket library
import random
import Adafruit_BBIO.ADC as ADC
from Adafruit_BNO055 import BNO055
import socket
import subprocess
import time
import datetime

#sensor pin connection
pin_pulse_raw="P9_40";
pin_eda_raw="P9_33";

# Select data to be streamed
ON_accel_x=1;
ON_accel_y=1;
ON_accel_z=1;
ON_accel_linear=0;
ON_gyro_yaw=0;
ON_gyro_roll=0;
ON_gyro_pitch=0;
ON_pulse_raw=1;
ON_eda_raw=1;
ON_temp_raw=1;

#sensor data
accel_x=0;
accel_y=0;
accel_z=0;
accel_linear=0;
gyro_yaw=0;
gyro_roll=0;
gyro_pitch=0;
pulse_raw=0;
pulse_proc=0;
eda_raw=0;
temp_raw=0;

# Setup ADC and measure first few values to set threshold
ADC.setup()
edaSum=0;
for x in range(0, 500):
    edaSum+=ADC.read(pin_eda_raw)
threshold=edaSum/500;

#setup accelerometer
bno=BNO055.BNO055(rst='P9_12')

if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor     connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')
##########################################################################################################
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
reply="OK"
min_pulse_raw=4096
max_pulse_raw=0
avg_pulse_raw=0
pulse_counted = False
pulse_count=0
pulse_startTime=0;
pulse_endTime=0;
pulse_bpm=0
pulse_totalCount=0;
pulse_totalBpm=0;
pulse_time=0;
pulse_MaxCount=5;
pulse_avg=0;
while True:
    start = time.time()
    # Establish connection with client.
# send a thank you message to the client.
    p = subprocess.Popen("./cpu_temp", stdout=subprocess.PIPE, shell=True)
    (temp, err)=p.communicate()
    p.wait()
    #c.send(temp.strip()+"$")
    #accel_x=random.uniform(-20,20);
    #accel_y=random.uniform(-20,20);
    #accel_z=random.uniform(-20,20);
    #accel_linear=random.uniform(1.5,1.9);
    #gyro_yaw=random.uniform(1.5,1.9);
    #gyro_roll=random.uniform(1.5,1.9);
    #gyro_pitch=random.uniform(1.5,1.9);
    #pulse_raw=random.uniform(-100,100);
    #######################################################################
    pulse_raw=ADC.read_raw(pin_pulse_raw)
    if min_pulse_raw > pulse_raw:
        min_pulse_raw=pulse_raw
    if max_pulse_raw < pulse_raw:
        max_pulse_raw=pulse_raw

    avg_pulse_raw=(min_pulse_raw+max_pulse_raw)/2;
    #min_pulse_raw=avg_pulse_raw
    #max_pulse_raw=avg_pulse_raw
    if pulse_raw >= max_pulse_raw:
        pulse_proc = 1
    else:
        pulse_proc = 0.8

    if pulse_proc == 1 and pulse_counted == False:
        pulse_counted = True;
        pulse_count+=1;

    if pulse_proc < 1 and pulse_counted == True:
        pulse_counted = False

    if pulse_count == 0:
        pulse_startTime = time.time()

    if pulse_count ==pulse_MaxCount:
        pulse_endTime = time.time();
        deltaTime = pulse_endTime - pulse_startTime;
        pulse_bpm=pulse_MaxCount*60/deltaTime;
        pulse_totalCount+=pulse_MaxCount;
        pulse_totalBpm+=pulse_bpm;
        pulse_avg=pulse_totalBpm/pulse_totalCount;
        print(str(pulse_avg)+"\t"+str(pulse_totalBpm)+"\t"+str(pulse_totalCount)+"\n");
        pulse_count=0;

    #######################################################################

    #######################################################################
    eda_raw=ADC.read_raw(pin_eda_raw)
    #######################################################################

    #######################################################################
    accel_x,accel_y,accel_z = bno.read_accelerometer()
    # BNO055 Sensor temperature in degrees Celsius:
    #temp_c = bno.read_temp()
    #######################################################################
    temp_raw=random.uniform(1.5,1.9);

    if ON_temp_raw == 1:
        #output=temp.strip()+";";
        output=str(pulse_count)+";";

    if ON_pulse_raw == 1:
        output+=str(pulse_proc)+";";

    if ON_eda_raw == 1:
        output+=str(pulse_raw)+";";

    if ON_accel_linear == 1:
        output+=str(accel_linear)+";";

    if ON_accel_x == 1:
        output+=str(pulse_avg)+";";
       #output+=str(accel_x)+";";

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
    if reply == "OK":
        c.send(output+"$");
    if not reply: break
    reply = c.recv(4096)
    print(output+"\t :"+reply+"\n")
    #print(end - start)
    count=count+1
    #time.sleep(1);
# Close the connection with the client
c.close()
