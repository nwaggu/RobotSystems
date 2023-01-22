import picarx_improved as picar
import time

#Moves the picar forward and back 
def moveBackAndForth(px):
    px.forward(50)
    time.sleep(1)
    px.backward(50)
    px.stop()

def kTurn(px):
    speed = 70
    angle = 35
    #Right Turn
    px.set_dir_servo_angle(35)
    px.forward(70)
    time.sleep(1)
    px.stop()
    #Left Turn Out
    px.set_dir_servo_angle(-35)
    px.backward(70)
    time.sleep(1)
    px.stop()
    #Right Turn foward
    px.set_dir_servo_angle(35)
    px.forward(30)
    time.sleep(1)
    px.stop()
    
    
if __name__ == "__main__":
    px = picar.Picarx()
    kTurn(px)

    
    
    