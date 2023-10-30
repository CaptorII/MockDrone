from djitellopy import TelloSwarm

swarm = TelloSwarm.fromIps([
    "127.0.0.1"
], [8890], [8990])

swarm.connect()
swarm.takeoff()

# run in parallel on all tellos
# 同时在所有Tello上执行
swarm.move_up(100)

# run by one tello after the other
# 让Tello一个接一个执行
swarm.sequential(lambda i, tello: tello.move_forward(i * 20 + 20))

# making each tello do something unique in parallel
# 让每一架Tello单独执行不同的操作
swarm.parallel(lambda i, tello: tello.move_left(i * 100 + 20))

swarm.land()
swarm.end()
