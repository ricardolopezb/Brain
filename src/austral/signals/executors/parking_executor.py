import time

from src.austral.configs import BASE_SPEED, PARKING_SPEED, IS_ABLE_TO_PARK
from src.utils.messages.allMessages import SpeedMotor, Control


class ParkingExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING PARKING SEQUENCE ###")
        if IS_ABLE_TO_PARK:
            print("### PARKING ###")

        time.sleep(3)
        speed = PARKING_SPEED

        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        time.sleep(2)

        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 3, 'Steer': 22.0}
        })
        time.sleep(3)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 3, 'Steer': -22.0}
        })
        time.sleep(3)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1, 'Steer': 10}
        })
        time.sleep(1)

        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 1, 'Steer': -3}
        })
        time.sleep(1)

        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': -22.0}
        })
        time.sleep(1.5)

        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': 22.0}
        })
        time.sleep(1.5)

        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
