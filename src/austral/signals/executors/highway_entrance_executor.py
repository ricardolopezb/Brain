from src.austral.configs import BASE_SPEED
from src.utils.messages.allMessages import SpeedMotor


class HighwayEntranceExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING HIGHWAY ENTRANCE SEQUENCE ###")
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED + 3
        })
