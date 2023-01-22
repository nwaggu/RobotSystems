import picarx_improved as picar
import time

if __name__ == "__main__":
    px = picar.Picarx()
    px.set_dir_servo_angle(0)
    px.forward(50)
    time.sleep(1)
    px.stop()
