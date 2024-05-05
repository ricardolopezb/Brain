import time

from src.austral.configs import set_new_votes_logic, BASE_SPEED, STOP_DURATION
from src.utils.messages.allMessages import SteerMotor, SpeedMotor


class StopExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING STOP SEQUENCE ###")
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })

        time.sleep(STOP_DURATION)
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })

        queue_list['Warning'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": -22
        })
        set_new_votes_logic(True)
