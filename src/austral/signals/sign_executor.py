import time

from src.utils.messages.allMessages import SpeedMotor, Control


class SignExecutor:
    def __init__(self, queue_list):
        self.just_seen_sign = None
        self.queue_list = queue_list

    def execute(self, sign):
        if sign == self.just_seen_sign:
            return
        if sign == "crosswalk":
            print("FOUND A CROSSWALK")
        elif sign == "parking":
            self.send_parking_sequence()
        elif sign == "stop":
            self.send_stop_sequence()
        elif sign == "yield":
            print("FOUND A YIELD")
        print("SETTING JUST SEEN SIGN TO", sign)

        self.just_seen_sign = sign

    def send_parking_sequence(self):
        print("SENDING PARKING SEQUENCE")
        speed = 20.0
        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1, 'Steer': -2.8}
        })
        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 2, 'Steer': 22.0}
        })

        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 2, 'Steer': -22.0}
        })

        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1, 'Steer': -2.8}
        })

        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 1, 'Steer': -4.0}
        })

        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': -22.0}
        })

        self.queue_list['Warning'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': 22.0}
        })

        # self.MySendCommand(speed, -2.8, 1.0)
        # self.MySendCommand(-speed, 22.0, 2)
        # self.MySendCommand(-speed, -22.0, 2)
        # self.MySendCommand(speed, -2.8, 1)
        # self.MySendCommand(-speed, -4.0, 1)
        # self.MySendCommand(speed, -22.0, 1.5)
        # self.MySendCommand(speed, 22.0, 1.5)

    def send_stop_sequence(self):
        # self.queue_list['Critical'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': 0, 'Time': 3, 'Steer': 0}
        # })
        self.queue_list['Warning'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        time.sleep(3)
        self.queue_list['Warning'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 5
        })
