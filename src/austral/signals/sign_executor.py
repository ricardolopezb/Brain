import time

from src.austral.api.data_sender import DataSender
from src.austral.configs import BASE_SPEED, LOW_SPEED, CROSSWALK_EXECUTION_DURATION, STOP_DURATION, PARKING_SPEED, \
    set_new_votes_logic
from src.utils.messages.allMessages import SpeedMotor, Control, SteerMotor
from multiprocessing import Queue

class SignExecutor:
    def __init__(self, queue_list):
        self.just_seen_sign = None
        self.queue_list = queue_list
        self.parking_seen = False

    def execute(self, sign):
        if sign == self.just_seen_sign:
            return
        # if self.just_seen_sign == 'stop' and sign is None:
        #     self.send_stop_sequence()
        if sign == 'stop':
            self.send_stop_sequence()

        # elif self.just_seen_sign == 'parking' and sign is None:
        #     self.send_parking_sequence()
        elif sign == 'parking':
            self.send_parking_sequence()

        elif sign == "crosswalk":
            self.send_crosswalk_sequence()
        elif sign == "yield":
            print("FOUND A YIELD")

        print("SETTING JUST SEEN SIGN TO", sign)
        self.just_seen_sign = sign

    def send_parking_sequence(self):
        if self.parking_seen:
            return

        # self.queue_list = {
        #     'Critical': Queue(),
        #     'Warning': Queue(),
        #     'General': Queue(),
        #     'Config': self.queue_list['Config'],
        # }
        time.sleep(3)

        print("SENDING PARKING SEQUENCE")
        # self.queue_list['Critical'].put({
        #     "Owner": SpeedMotor.Owner.value,
        #     "msgID": SpeedMotor.msgID.value,
        #     "msgType": SpeedMotor.msgType.value,
        #     "msgValue": 0
        # })

        speed = PARKING_SPEED

        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        time.sleep(2)

        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': speed, 'Time': 0.5, 'Steer': -5}
        # })
        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 3, 'Steer': 22.0}
        })
        time.sleep(3)
        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 3, 'Steer': -22.0}
        })
        time.sleep(3)
        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1, 'Steer': -3}
        })
        time.sleep(1)

        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 1, 'Steer': -3}
        })
        time.sleep(1)

        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': -22.0}
        })
        time.sleep(1.5)

        self.queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': 22.0}
        })
        time.sleep(1.5)

        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
        self.parking_seen = True


    def send_stop_sequence(self):
        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        DataSender.send('/speed', {'speed': 0})
        time.sleep(STOP_DURATION)
        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
        DataSender.send('/speed', {'speed': BASE_SPEED})
        self.queue_list['Warning'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": -22
        })
        DataSender.send('/steer', {'steer': -22})
        set_new_votes_logic(True)

    def send_crosswalk_sequence(self):
        print("############### LOWERING SPEED")
        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": LOW_SPEED
        })
        DataSender.send('/speed', {'speed': LOW_SPEED})
        time.sleep(CROSSWALK_EXECUTION_DURATION)
        print("############### INCREASING SPEED")
        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
        DataSender.send('/speed', {'speed': BASE_SPEED})
