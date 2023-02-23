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
        print("start read")
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        print(self.ec)
        while self.echo.value()==0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value()==1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                print("returned negative 1")
                return -1
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        print("cm")
        return cm

    def read(self, times=10):
        for i in range(times):
            a = self._read()
            if a != -1:
                return a
        return -1

if __name__=='__main__':
    car = px.Picarx()
    while True:
        print(car.get_grayscale_data())
        print(car.get_distance())
        