import time
from enum import Enum
import logging
try:
    from robot_hat import ADC
    from robot_hat import Grayscale_Module, Ultrasonic
    from robot_hat.utils import reset_mcu
    reset_mcu()
    time.sleep (0.01)
except ImportError:
    print ("This computer does not appear to be a PiCar -X system (robot_hat is not present). Shadowing hardware calls with substitute functions ")
    from sim_robot_hat import *

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
from picarx_improved import Picarx
from concurrency import Bus
import concurrent.futures





class CameraSensor(object):
    
    def __init__(self, line_color='blue'):
        
        self.color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[165,180]}  #Here is the range of H in the HSV color space represented by the color
        self.kernel_5 = np.ones((5,5),np.uint8) #Define a 5×5 convolution kernel with element values of all 1.
        self.line_color= line_color

    def read(self, img):

        # The blue range will be different under different lighting conditions and can be adjusted flexibly.  H: chroma, S: saturation v: lightness
        resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)  # In order to reduce the amount of calculation, the size of the picture is reduced to (160,120)
        hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # Convert from BGR to HSV
        color_type = self.line_color
        
        mask = cv2.inRange(hsv,np.array([min(self.color_dict[color_type]), 60, 60]), np.array([max(self.color_dict[color_type]), 255, 255]) )           # inRange()：Make the ones between lower/upper white, and the rest black
        if color_type == 'red':
                mask_2 = cv2.inRange(hsv, (self.color_dict['red_2'][0],0,0), (self.color_dict['red_2'][1],255,255)) 
                mask = cv2.bitwise_or(mask, mask_2)

        morphologyEx_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel_5,iterations=1)              # Perform an open operation on the image 

        # Find the contour in morphologyEx_img, and the contours are arranged according to the area from small to large.
        _tuple = cv2.findContours(morphologyEx_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)      
        # compatible with opencv3.x and openc4.x
        if len(_tuple) == 3:
            _, contours, hierarchy = _tuple
        else:
            contours, hierarchy = _tuple
        
        color_area_num = len(contours) # Count the number of contours

        #Get position of detected contour on map
        if color_area_num > 0: 
            i = contours[0]    # Traverse all contours
            x,y,w,h = cv2.boundingRect(i)      # Decompose the contour into the coordinates of the upper left corner and the width and height of the recognition object

                # Draw a rectangle on the image (picture, upper left corner coordinate, lower right corner coordinate, color, line width)
            if w >= 8 and h >= 8: # Because the picture is reduced to a quarter of the original size, if you want to draw a rectangle on the original picture to circle the target, you have to multiply x, y, w, h by 4.
                x = x * 4
                y = y * 4 
                w = w * 4
                h = h * 4
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)  # Draw a rectangular frame
                cv2.putText(img,color_type,(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)# Add character description
                coords = (x,y,w,h)
                return img, coords

        return img, (0,0,0,0)
    
    def producer(self, bus:Bus, delay):
        with PiCamera() as camera:
            print("Starting Camera Line Following, 2 Second delay before start")
            print("Use VNC to see camera perspective")
            print("By default BLUE lines are followed.")
            camera.resolution = (640,480)
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)
            #Repeat for every frame
            for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):# use_video_port=True
                img = frame.array
                #Get sensor/camera output data
                new_img, sensorOutput = self.read(img)
                bus.write(sensorOutput)
                #Show what car is seeing
                cv2.imshow("video", new_img)    # OpenCV image show
                rawCapture.truncate(0)   # Release cache
            
                k = cv2.waitKey(1) & 0xFF
                # 27 is the ESC key, which means that if you press the ESC key to exit
                if k == 27:
                    break
                time.sleep(delay)
            print('quit ...') 
            cv2.destroyAllWindows()
            camera.close()
            


class CameraInterpreter(object):
    def __init__(self, sensitivity=20):
        self.current_center = (0,0,0,0)
        self.sensitivity = sensitivity
    
    def ouputPosition(self, sensor_data):
        if sensor_data == (0,0,0,0):
            print("Line not detected")
            return 0
        #Add the x distance plus half the mapped rectangle's width to get rectangle center
        midpoint_x = sensor_data[0] + sensor_data[2]/2
        edge_one = 320-self.sensitivity
        edge_two = 320+self.sensitivity
        #Check if off center (320,240)
        if not edge_one <= midpoint_x <= edge_two:
            if midpoint_x >= 320:
                return 1*(midpoint_x-320)/320
            else:
                return -1*(320-midpoint_x)/320
        return 0
    
    def producer_consumer(self, sensor_bus:Bus, interpreter_bus:Bus, delay):
        while True:
            sensor_data = sensor_bus.read()
            position = self.ouputPosition(sensor_data)
            interpreter_bus.write(position)
            time.sleep(delay)

class CameraController(object):
    def __init__(self, scaling=0, angle=35):
        self.scaling = scaling
        self.angle = angle
        
        #Setup car to follow line
        self.car = Picarx()
        self.car.set_camera_servo1_angle(0)
        self.car.set_camera_servo2_angle(-20)
        self.car.set_dir_servo_angle(0)
    
    def steer(self, scaling):
        self.scaling = scaling*2
        directed_angle = self.scaling*self.angle
        self.car.set_dir_servo_angle(directed_angle)
        return directed_angle

    def moveForward(self): 
        self.car.forward(25)
    
    def consumer(self, bus:Bus, delay):
        self.moveForward()
        while True:
            interpret_data = bus.read()
            self.steer(interpret_data)
            time.sleep(delay)

def cameraOnLine():
    #Class and Delay Setups
    sensor = CameraSensor()
    interpreter = CameraInterpreter()
    controller = CameraController()
    sensor_values_bus = Bus((0,0,0,0))
    interpreter_bus = Bus(0) 
    sensor_delay = 0.2
    interpreter_delay = 0.2
    controller_delay = 0.2

    with concurrent.futures.ThreadPoolExecutor(max_workers =3) as executor:
            eSensor = executor.submit(sensor.producer,sensor_values_bus, sensor_delay)
            eInterpreter = executor.submit(interpreter.producer_consumer,sensor_values_bus,interpreter_bus,interpreter_delay)
            eController = executor.submit(controller.consumer, interpreter_bus, controller_delay)
    eSensor.result()
    eInterpreter.result()
    eController.result()

#Main Script
if __name__=='__main__':
    try:
        logging.debug("Starting greyscale line following script")
        cameraOnLine()
        
    except KeyboardInterrupt:
        logging.debug("Forced to end")  