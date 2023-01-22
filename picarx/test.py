import picarx_improved as picar
import time

#Moves the picar forward and back 
def moveBackAndForth(px):
    px.set_dir_servo_angle(0)
    #Move forward
    px.forward(50)
    time.sleep(1)
    px.stop()
    #Move back
    px.backward(50)
    time.sleep(1)
    px.stop()
    return True

def kTurn(px):
    px.set_dir_servo_angle(0)
    speed = 70
    angle = 30
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
    px.forward(30)
    time.sleep(1.5)
    px.stop()
    return True
    
def parallelParkingRight(px):
    px.set_dir_servo_angle(0)
    #Inch backwards for space
    px.backward(20)
    time.sleep(1)
    px.stop()
    #Turn left into spot
    px.set_dir_servo_angle(10)
    px.backward(20)
    time.sleep(2)
    px.stop()
    #Straighten out car
    px.set_dir_servo_angle(-10)
    px.backward(20)
    time.sleep(2)
    px.stop()
    return True

def parallelParkingLeft(px):
    px.set_dir_servo_angle(0)
    px.backward(20)
    time.sleep(1)
    px.stop()
    px.set_dir_servo_angle(-10)
    px.backward(20)
    time.sleep(2)
    px.stop()
    px.set_dir_servo_angle(10)
    px.backward(20)
    time.sleep(2)
    px.stop()
    return True


    
if __name__ == "__main__":
    px = picar.Picarx()
    running = True
    while running:
        #Print Menu
        print('Select a motion')
        print("a: K-Turn")
        print("b: Forward and Back")
        print("c: Parrallel Park Left")
        print("d: Parallel Part Right")
        print("e: Quit")
        #Get User input
        user_input = input("Select a menu option: ")
        passed = False
        if user_input =="a": 
                print("K Turn Chosen")
                passed = kTurn(px)
        elif user_input =="b":
                print("Forward and Back Chosen")
                passed = moveBackAndForth(px)
        elif user_input =="c": 
                print("Parallel Park Left Chosen")
                passed = parallelParkingLeft(px)
        elif user_input =="d":
                print("Parallel Park Right Chosen")
                passed = parallelParkingRight(px)
        elif user_input =="e":
                running = False
                print("Quit Chosen")
        else:
                print("Invalid input")
        if passed and running:
            print("Car executed manuever successfully. Awaiting new input...")
        elif not running:
            print("Exiting script...")
        else:
            print("Something went wrong!")
    print("Exit Successful")

    
    
    