from djitellopy import Tello

tello = Tello(host="127.0.0.1", control_port=8890, state_port=8990)

tello.connect()
tello.takeoff()

tello.move_left(100)
tello.rotate_clockwise(90)
tello.move_forward(100)

tello.land()
