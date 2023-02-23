import time 
try:
    from robot_hat import Pin, PWM, Servo, fileDB
    from robot_hat import Grayscale_Module, Ultrasonic
    from robot_hat.utils import reset_mcu
    reset_mcu()
    time.sleep (0.01)
except ImportError:
    print ("This computer does not appear to be a PiCar -X system (robot_hat is not present). Shadowing hardware calls with substitute functions ")
    from sim_robot_hat import *
import picarx_improved as px
       
class UltraSonicSensor():
    def __init__(self,ultrasonic_pins:list=['D2','D3'], timeout=0.02):
        trig, echo= ultrasonic_pins        
        self.trig = Pin(trig)
        self.echo = Pin(echo)
        self.timeout = timeout
    
    def _read(self):
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while self.echo.value()==0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value()==1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        return cm

    def read(self, times=10):
        print("I read")
        for i in range(times):
            a = self._read()
            if a != -1:
                return a
        return -1


class UltraInterpreter():
    def __init__(self):
        self.stopping_distance = 10
    
    def determineGo(self, distance):
        if distance <= self.stopping_distance:
            print("False!")
            return False 
        print("Impossible")
        return True


class UltraController():
    def __init__(self, car:px.Picarx):
        self.car:px.Picarx = car 
    
    def drive(self, go):
        if go:
            print("Not here")
            self.car.forward(30)
        else:
            print("You Are here")
            self.car.stop()


if __name__=='__main__':
    car = px.Picarx()
    while True:
        print(car.get_distance())
        