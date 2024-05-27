from src.austral.configs import BASE_SPEED
from src.utils.messages.allMessages import SpeedMotor


class RoundaboutExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING ROUNDABOUT SEQUENCE ###")
