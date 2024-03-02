from src.utils.messages.allMessages import SpeedMotor, Control


class SignExecutor:
    def __init__(self, queue_list):
        self.queue_list = queue_list

    def execute(self, sign):
        if sign == "crosswalk":
            print("FOUND A CROSSWALK")
        elif sign == "parking":
            self.send_parking_sequence()
        elif sign == "stop":
            self.send_stop_sequence()
        elif sign == "yield":
            print("FOUND A YIELD")

    def send_parking_sequence(self):
        print("SENDING PARKING SEQUENCE")

    def send_stop_sequence(self):
        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': 0, 'Time': 3, 'Steer': 0}
        })
        self.queue_list['Warning'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 10
        })
