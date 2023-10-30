import logging
import random
import socket
import socketserver
import threading
import time
from dataclasses import dataclass

# set up logging
HANDLER = logging.StreamHandler()
FORMATTER = logging.Formatter(
    '[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER = logging.getLogger('drone_server')
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class Drone:
    s_pitch: int = 0
    s_roll: int = 0
    s_yaw: int = 0
    s_vgx: int = 0
    s_vgy: int = 0
    s_vgz: int = 0
    s_templ: int = 0
    s_temph: int = 0
    s_tof: int = 0
    s_h: int = 0  # height in cm
    s_bat: int = 100  # percent current battery
    s_baro: float = 0.0
    s_time: int = 0
    s_agx: float = 0.0
    s_agy: float = 0.0
    s_agz: float = 0.0
    s_end: str = "\r\n"

    def __str__(self):
        LOGGER.info(f"id: {id(self)}; Height: {self.s_h}")
        return (''.join(f'{item[2:]}: {getattr(self, item)}; '
                        for item in dir(type(self))
                        if item.startswith('s_') and item != 's_end')
                )[:-1] + self.s_end

    def dispatcher(self, cmd: bytes) -> str:
        """provides staging for pretending to respond to commands"""
        LOGGER.debug("Initiating Dispatcher command: %s", cmd)
        command = str(cmd, 'utf-8')
        time.sleep(random.randint(0, 4))
        
        # drain the battery a bit each time but ensure it doesn't drop below 0
        self.s_bat = max(self.s_bat - random.randint(0, 5), 0)

        match command.split():
            case ["takeoff"]:
                LOGGER.debug("TAKEOFF: Vroom Vroom Taking Off")
                time.sleep(3)
                self.s_h += 100
                LOGGER.debug(f"id: {id(self)}; Height: {self.s_h}")
                return "ok"

            case ["command"]:
                LOGGER.debug("COMMAND (command): %s", command)
                return "ok"

            case ["left", amount]:
                self.s_yaw += int(amount)
                LOGGER.debug(f"Turning left by {amount}.")
                return "ok"

            case ["cw", amount]:
                self.s_yaw -= int(amount)
                LOGGER.info(f"Turning right by {amount}.")
                return "ok"

            case ["land"]:
                LOGGER.info("LANDING: Whoosh. Clean landing.")
                time.sleep(2)
                self.s_h = 0
                return "ok"

            case _:
                LOGGER.info("OTHER COMMAND (command): %s", command)
                return "ok"


class DroneEndPoint(socketserver.BaseRequestHandler):
    """Echoes text requests from client and eventually provides a handler for some of them. 
    Responses are delayed randomly """
    drones = {}

    STATE_PORT = 8990

    def send_state_information(self, refresh_interval: int = 3) -> None:
        while True:
            drone_state = str(self.drones[self.client_address])
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                # Using 'with' ensures the socket is properly closed after sending data
                sock.sendto(
                    bytes(drone_state, "utf-8"),
                    (self.client_address[0], self.STATE_PORT)
                )
            LOGGER.info(f"Sent:     {drone_state}")
            time.sleep(refresh_interval)

    def handle(self) -> None:
        if self.client_address not in self.drones:
            self.drones[self.client_address] = Drone()

        data = self.request[0].strip()
        s = self.request[1]

        # DEBUG and logging omitted for brevity

        # get drone's response
        response = self.drones[self.client_address].dispatcher(data)
        s.sendto(bytes(response, 'utf-8'), self.client_address)

        LOGGER.info(f"Sent Response: {response}")

        # Fixed the threading issue here
        state_thread = threading.Thread(target=self.send_state_information)
        state_thread.daemon = True
        state_thread.start()


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

def main():
    print("WELCOME TO MOCK xDRONE: \nI pretend to be a drone so you don't have to.")
    # 8999 is NOT the default Tello drone port. Update tello.py accordingly
    HOST, PORT = "127.0.0.1", 8890
    server = ThreadedUDPServer((HOST, PORT), DroneEndPoint)
    with server:
        ip, port = server.server_address
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        while True:
            pass

if __name__ == "__main__":
    main()