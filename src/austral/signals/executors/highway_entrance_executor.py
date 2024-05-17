from src.austral.configs import BASE_SPEED, HIGHWAY_ADDITIONAL_SPEED
from src.utils.messages.allMessages import SpeedMotor, IsInHighway, ShouldHandleFrontUltrasonic


class HighwayEntranceExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING HIGHWAY ENTRANCE SEQUENCE ###")
        queue_list['Critical'].put({
            "Owner": IsInHighway.Owner.value,
            "msgID": IsInHighway.msgID.value,
            "msgType": IsInHighway.msgType.value,
            "msgValue": {"isInHighway": True}
        })
        queue_list['Critical'].put({
            "Owner": ShouldHandleFrontUltrasonic.Owner.value,
            "msgID": ShouldHandleFrontUltrasonic.msgID.value,
            "msgType": ShouldHandleFrontUltrasonic.msgType.value,
            "msgValue": {'value': True}
        })
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED + HIGHWAY_ADDITIONAL_SPEED
        })

