#!/usr/bin/python3
import rossros as rr
import logging
import time
import math
from greyscale_on_line import PicarxSensor, Interpreter, Controller
from picarx_improved import Picarx
from ultrasonic import UltraController, UltraInterpreter, UltraSonicSensor
# logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

#Greyscale Control
car = Picarx()
greyscale_sensor = PicarxSensor()
greyscale_interpreter = Interpreter()
greyscale_control = Controller(car=car) 

#UltraSonic Control
ultra_sensor = UltraSonicSensor()
ultra_interpreter = UltraInterpreter()
ultra_controller = UltraController(car=car)


""" Create buses for passing data """
# Initiate data and termination busses
greyscale_bus = rr.Bus(greyscale_sensor.read_greyscale_data(),"Greyscale Bus")
steer_bus = rr.Bus(0, "Steer Bus")
bTerminate = rr.Bus(0, "Termination Bus")

ultra_bus = rr.Bus(0, "UltraSonic Bus")
forward_bus = rr.Bus(False, "Foward Bus")


""" Create P/PC/C """
# Reads Greyscale data
readGreyScale = rr.Producer(
    greyscale_sensor.read_greyscale_data,  # function that will generate data
    greyscale_bus,  # output data bus
    0.2,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read greyscale data")

# Determines direction
directionDictator = rr.ConsumerProducer(
    greyscale_interpreter.outputPosition,  # function that will process data
    greyscale_bus,  # input data buses
    steer_bus,  # output data bus
    0.5,  # delay between data control cycles
    bTerminate,  # bus to watch for termination signal
    "Direction Dictator")

#Controls steering
steeringControl = rr.Consumer(
    greyscale_control.steer,  # function that will process data
    steer_bus,  # input data buses
    0.5,  # delay between data control cycles
    bTerminate,  # bus to watch for termination signal
    "Steering control")

#Reads ultrasonic
readUltra = rr.Producer(
    ultra_sensor.read,  # function that will generate data
    ultra_bus,  # output data bus
    0.5,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read ultrasonic sensor")

# Says to go forward
decideForward = rr.ConsumerProducer(
    ultra_interpreter.determineGo,  # function that will process data
    ultra_bus,  # input data buses
    forward_bus,  # output data bus
    0.5,  # delay between data control cycles
    bTerminate,  # bus to watch for termination signal
    "Decide when to go forward")

#Moves forwards
goForward = rr.Consumer(
    ultra_controller.drive,  
    forward_bus,  
    0.2,  
    bTerminate,  
    "Go Forward")

""" Fourth Part: Create RossROS Timer objects """
# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
terminationTimer = rr.Timer(
    bTerminate,  # Output data bus
    60,  # Duration
    0.2,  # Delay between checking for termination time
    bTerminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

""" Fifth Part: Concurrent execution """

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [
                          readGreyScale,
                          directionDictator,
                          steeringControl,readUltra,
                          goForward, decideForward,
                          terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
