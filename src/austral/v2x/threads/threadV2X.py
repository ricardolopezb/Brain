import threading
from multiprocessing import Pipe
from src.hardware.serialhandler.threads.messageconverter import MessageConverter
from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (
    SignalRunning,
    Cars,
    Semaphores
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

        self.coordinates_log_file = open(f'{int(time.time())}.txt', "w")


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
                    #print(f"Received CARS -> {message}")
                    x = message['value']['x']
                    y = message['value']['y']
                    print("LOGGING:", f'{x};{y}\n')
                    self.coordinates_log_file.write(f'{x};{y}\n')


                if self.pipeRecvSemaphores.poll():
                    message = self.pipeRecvSemaphores.recv()
                    print(f"Received SEMAPHORES -> {message}")

            except Exception as e:
                print(e)

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
