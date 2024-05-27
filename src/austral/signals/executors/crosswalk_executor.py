import time

from src.austral.configs import LOW_SPEED, CROSSWALK_EXECUTION_DURATION, BASE_SPEED
from src.utils.messages.allMessages import SpeedMotor


class CrosswalkExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING CROSSWALK SEQUENCE ###")
        print("############### LOWERING SPEED")
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": LOW_SPEED
        })
        time.sleep(CROSSWALK_EXECUTION_DURATION)
        print("############### INCREASING SPEED")
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
