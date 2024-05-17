import time

from src.utils.messages.allMessages import SteerMotor


class OvertakeManouverExecutor:
    @staticmethod
    def execute(queue_list):
        print("### EXECUTING OVERTAKE MANOUVER SEQUENCE ###")
        queue_list['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": -11
        })
        time.sleep(1.5)
        queue_list['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": 11
        })
        time.sleep(0.75)
        queue_list['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": -3
        })
        time.sleep(8)
        queue_list['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": 11
        })
        time.sleep(1)
        queue_list['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": -3
        })
