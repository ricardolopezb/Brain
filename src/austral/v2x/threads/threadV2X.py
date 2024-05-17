import os
import threading
from multiprocessing import Pipe

from src.austral.configs import MY_CAR_ID, V2X_SEMAPHORE_INFLUENCE_RADIUS, BASE_SPEED, V2X_SEMAPHORE_COOLDOWN
from src.hardware.serialhandler.threads.messageconverter import MessageConverter
from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (
    SignalRunning,
    Cars,
    Semaphores, SpeedMotor
)
import time


class threadV2X(ThreadWithStop):
    """This thread manages the data from the V2X server.\n

    Args:
        queues (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
        serialCom (serial.Serial): Serial connection between the two boards.
        logFile (FileHandler): The path to the history file where you can find the logs from the connection.
        example (bool, optional): Flag for exmaple activation. Defaults to False.
    """

    # ===================================== INIT =========================================
    def __init__(self, queues):
        super(threadV2X, self).__init__()
        self.queuesList = queues

        self.messageConverter = MessageConverter()
        self.running = False
        pipeRecvCars, pipeSendCars = Pipe(duplex=False)
        self.pipeRecvCars = pipeRecvCars
        self.pipeSendCars = pipeSendCars

        pipeRecvSemaphores, pipeSendSemaphores = Pipe(duplex=False)
        self.pipeRecvSemaphores = pipeRecvSemaphores
        self.pipeSendSemaphores = pipeSendSemaphores

        self.my_car_id = MY_CAR_ID
        self.my_previous_coordinates = (0, 0)
        self.my_current_coordinates = (0, 0)

        self.last_time_semaphore_action_taken = time.time()

        self.logging_filename = f'{int(time.time())}.txt'
        self.subscribe()

    def subscribe(self):
        """Subscribe function. In this function we make all the required subscribe to process gateway"""
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Cars.Owner.value,
                "msgID": Cars.msgID.value,
                "To": {
                    "receiver": "threadV2X",
                    "pipe": self.pipeSendCars,
                },
            }
        )
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Semaphores.Owner.value,
                "msgID": Semaphores.msgID.value,
                "To": {
                    "receiver": "threadV2X",
                    "pipe": self.pipeSendSemaphores,
                },
            }
        )

    # ===================================== RUN ==========================================
    def run(self):
        """In this function we check if we got the enable engine signal. After we got it we will start getting messages from raspberry PI. It will transform them into NUCLEO commands and send them."""

        while self._running:
            try:
                if self.pipeRecvCars.poll():
                    message = self.pipeRecvCars.recv()
                    # print(f"Received CARS -> {message}")
                    x = float(message['value']['x'])
                    y = float(message['value']['y'])
                    if message['value']['id'] == self.my_car_id:
                        print("RECEIVED MY CAR COORDINATES IN Cars EVENT", message['value'])
                        self.log_my_coordinates(x, y)
                        self.my_previous_coordinates = self.my_current_coordinates
                        self.my_current_coordinates = (x, y)

                within_semaphore_cooldown = time.time() - self.last_time_semaphore_action_taken >= V2X_SEMAPHORE_COOLDOWN
                print('SEMAPHORE POLL', self.pipeRecvSemaphores.poll())
                print('SEMAPHORE COOLDOWN', within_semaphore_cooldown)
                if self.pipeRecvSemaphores.poll() and within_semaphore_cooldown:
                    message = self.pipeRecvSemaphores.recv()
                    print(f"Received SEMAPHORES -> {message}")
                    semaphore_x = float(message['value']['x'])
                    semaphore_y = float(message['value']['y'])

                    if self.is_not_within_semaphore_range(semaphore_x, semaphore_y):
                        print("## NO SEMAPHORE within range")
                        return
                    if self.is_moving_away_from_semaphore(semaphore_x, semaphore_y):
                        print("## MOVING AWAY FROM SEMAPHORE")
                        return
                    semaphore_state = message['value']['state']
                    if semaphore_state == 'green':
                        print("Found GREEN LIGHT, accelerating")
                        self.accelerate()
                    if semaphore_state == 'red':
                        print("Found RED LIGHT, braking")
                        self.brake()
                    self.last_time_semaphore_action_taken = time.time()

            except Exception as e:
                print(e)

    def is_not_within_semaphore_range(self, semaphore_x, semaphore_y):
        return self.calculate_distance(semaphore_x, semaphore_y, self.my_current_coordinates[0],
                                       self.my_current_coordinates[1]) > V2X_SEMAPHORE_INFLUENCE_RADIUS

    def is_moving_away_from_semaphore(self, semaphore_x, semaphore_y):
        return self.calculate_distance(semaphore_x, semaphore_y, self.my_current_coordinates[0], self.my_current_coordinates[1]) > self.calculate_distance(semaphore_x, semaphore_y, self.my_previous_coordinates[0], self.my_previous_coordinates[1])

    def brake(self):
        self.queuesList[SpeedMotor.Queue.value].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })

    def accelerate(self):
        self.queuesList[SpeedMotor.Queue.value].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })

    def calculate_distance(self, target_x, target_y, base_x, base_y):
        return ((float(target_x) - float(base_x)) ** 2 + (float(target_y) - float(base_y)) ** 2) ** 0.5

    def log_my_coordinates(self, x, y):
        mode = 'a' if os.path.exists(self.logging_filename) else 'w'
        with open(self.logging_filename, mode) as file:
            file.write(f'{x};{y}\n')

    # ==================================== START =========================================
    def start(self):
        super(threadV2X, self).start()

    # ==================================== STOP ==========================================
    def stop(self):
        """This function will close the thread and will stop the car."""
        print("STOPPING THE THREAD ********####*#*#*#*#*#*#*")
        self.coordinates_log_file.close()
        time.sleep(2)
        super(threadV2X, self).stop()
