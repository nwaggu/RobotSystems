import picarx_improved as picar
import time

#Moves the picar forward and back 
def moveBackAndForth(px):
    px.forward(50)
    time.sleep(1)
    px.backward(50)
    px.stop()

def kTurn(px):
    speed = 50
    angle = 35
    #Right Turn
    px.set_dir_servo_angle(angle)
    px.forward(speed)
    time.sleep(1)
    px.stop()
    #Left Turn Out
    px.set_dir_servo_angle(-angle)
    px.backward(speed)
    time.sleep(1)
    px.stop()
    #Right Turn foward
    px.set_dir_servo_angle(angle)
    px.forward(40)
    time.sleep(1)
    px.stop()
    #Move forward towards original postion
    px.forward(40)
    time.sleep(1)
    px.stop()
    
    
if __name__ == "__main__":
    px = picar.Picarx()
    kTurn(px)

    
    
    