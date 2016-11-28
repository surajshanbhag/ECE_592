#!/usr/bin/python
# first of all import the socket library
import random
from subprocess import call
import Adafruit_BBIO.ADC as ADC
from Adafruit_BNO055 import BNO055
import socket
import subprocess
import time
import datetime
import os

#sensor pin connection
pin_pulse_raw="P9_40";
pin_eda_raw="P9_33";

#sensor data
accel_x=0;
accel_y=0;
accel_z=0;
accel_linear=0;
gyro_yaw=0;
gyro_roll=0;
gyro_pitch=0;
pulse_raw=0;
eda_raw=0;
temp_raw=0;

min_pulse_raw=4096
max_pulse_raw=0
avg_pulse_raw=0
pulse_counted = False
pulse_count=0
pulse_startTime=0;
pulse_bpm=0
pulse_totalCount=0;
pulse_totalTime=0;
pulse_MaxCount=20;
pulse_avgBPM=0;
pulse_proc=0;

s=[];

edaSum=0;
eda_threshold=0;

bno=[]


def initialize_BNO():
    #setup accelerometer
    os.system("config-pin P9_17 i2c")
    os.system("config-pin P9_18 i2c")
    global bno
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

def initialize_Socket():
    # next create a socket object
    global s;
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

def init_EDA():
    global edaSum;
    global eda_threshold;
    edaSum=0;
    for x in range(0, 500):
        edaSum+=ADC.read(pin_eda_raw)
    eda_threshold=edaSum/500;

def get_Pulse():
    #######################################################################

    global pulse_raw;
    global pulse_proc;
    global min_pulse_raw;
    global max_pulse_raw;
    global avg_pulse_raw;
    global pulse_counted;
    global pulse_count;
    global pulse_startTime;
    global pulse_bpm;
    global pulse_totalCount;
    global pulse_totalTime;
    global pulse_MaxCount;
    global pulse_avgBPM;

    pulse_raw=ADC.read_raw(pin_pulse_raw)
    if min_pulse_raw > pulse_raw:
        min_pulse_raw=pulse_raw
    if max_pulse_raw < pulse_raw:
        max_pulse_raw=pulse_raw

    #avg_pulse_raw=(min_pulse_raw+max_pulse_raw)/2;
    avg_pulse_raw= 0.75*max_pulse_raw;

    if pulse_raw >= max_pulse_raw:
        pulse_proc = 1
    else:
        pulse_proc = 0.8  # 0.8 only to make display in GUI scalable , can be 0

    if pulse_proc == 1 and pulse_counted == False:
        pulse_counted = True;
        pulse_count+=1;

    if pulse_proc < 1 and pulse_counted == True:
        pulse_counted = False

    if pulse_count == 0:
        pulse_startTime = time.time()

    if pulse_count == pulse_MaxCount:
        deltaTime = time.time() - pulse_startTime;
        pulse_bpm=pulse_MaxCount*60/deltaTime;
        pulse_totalCount+=pulse_MaxCount;
        pulse_totalTime+=deltaTime;
        pulse_avgBPM=pulse_totalCount*60/pulse_totalTime;
        print(str(pulse_avgBPM)+"\t"+str(pulse_totalTime)+"\t"+str(pulse_totalCount)+"\n");
        pulse_count=0;
    #return pulse_raw,pulse_bpm,pulse_avgBPM;
        #######################################################################

averagedData=0
integratedData=0
seizureDetected=0
thresholdCount=0
if __name__ == "__main__":

    # Setup ADC and measure first few values to set threshold
    ADC.setup();
    init_EDA();

    initialize_BNO();
    initialize_Socket();

    count=0
    c, addr = s.accept()
    print 'Got connection from', addr
    reply="OK"

    pulse_totalTime =0;
    # a forever loop until we interrupt it or
    # an error occurs
    filename= time.strftime("%Y%m%d-%H%M%S")
    f=open("./datalog/"+filename,'w')

    while True:
        start = time.time()
        # Establish connection with client.
        # send a thank you message to the client.

        ######################
        #### RANDOM DATA #####
        ######################
        #p = subprocess.Popen("./cpu_temp", stdout=subprocess.PIPE, shell=True)
        #(temp, err)=p.communicate()
        #p.wait()
        #c.send(temp.strip()+"$")
        #accel_x=random.uniform(-20,20);
        #accel_y=random.uniform(-20,20);
        #accel_z=random.uniform(-20,20);
        #accel_linear=random.uniform(1.5,1.9);
        #gyro_yaw=random.uniform(1.5,1.9);
        #gyro_roll=random.uniform(1.5,1.9);
        #gyro_pitch=random.uniform(1.5,1.9);
        #pulse_raw=random.uniform(-100,100);
        #temp_raw=random.uniform(1.5,1.9);

        #######################################################################
        eda_raw=ADC.read_raw(pin_eda_raw)
        #######################################################################
        #get_Pulse();
        pulse_raw=ADC.read_raw(pin_pulse_raw)
        #######################################################################
        #accel_x,accel_y,accel_z = bno.read_accelerometer()
        accel_x,accel_y,accel_z = bno.read_linear_acceleration()
        resultantAccelration= ((accel_x**2)+(accel_y**2)+(accel_z**2))**0.5
        averagedData=(averagedData*count+resultantAccelration)/(count+1)
        integratedData=integratedData+resultantAccelration

        if resultantAccelration > 2:
            thresholdCount=thresholdCount+20
        elif thresholdCount > 0:
            thresholdCount=thresholdCount-20

        if thresholdCount > 1000:
            seizureDetected=1
        else:
            seizureDetected=0
        if count == 100:
            integratedData=0
            count=0;
        count=count +1
        # BNO055 Sensor temperature in degrees Celsius:
        temp_c = bno.read_temp()
        #######################################################################

        output=str(temp_c)+";";#0
        output+=str(pulse_raw)+";";#1
        output+=str(eda_raw)+";";#2
        output+=str(accel_x)+";";#3
        output+=str(accel_y)+";";#4
        output+=str(accel_z)+";";#5
        output+=str(resultantAccelration)+";";#6
        output+=str(seizureDetected)+";";#7
        output+=str(thresholdCount)+";";#8
        end = time.time()
        f.write(output+"\n")
        if reply == "OK":
            c.send(output+"$");
        if not reply: break
        reply = c.recv(4096)
        print(output+"\t :"+reply+"\n")
        #print(end - start)
        #time.sleep(1);
# Close the connection with the client
    c.close()
    f.close()

