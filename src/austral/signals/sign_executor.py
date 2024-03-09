import time

from src.austral.api.data_sender import DataSender
from src.austral.configs import BASE_SPEED, LOW_SPEED, CROSSWALK_EXECUTION_DURATION, STOP_DURATION, PARKING_SPEED
from src.utils.messages.allMessages import SpeedMotor


class SignExecutor:
    def __init__(self, queue_list):
        self.just_seen_sign = None
        self.queue_list = queue_list

    def execute(self, sign):
        if sign == self.just_seen_sign:
            return
        # if self.just_seen_sign == 'stop' and sign is None:
        #     self.send_stop_sequence()
        if sign == 'stop':
            self.send_stop_sequence()

        elif self.just_seen_sign == 'parking' and sign is None:
            self.send_parking_sequence()

        elif sign == "crosswalk":
            self.send_crosswalk_sequence()
        elif sign == "yield":
            print("FOUND A YIELD")
        elif sign is None:
            DataSender.send('/sign', {'sign': None})

        print("SETTING JUST SEEN SIGN TO", sign)
        self.just_seen_sign = sign

    def send_parking_sequence(self):
        DataSender.send('/sign', {'sign': 'Parking'})
        print("SENDING PARKING SEQUENCE")
        self.queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        # speed = PARKING_SPEED
        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': -speed, 'Time': 2, 'Steer': 22.0}
        # })
        #
        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': -speed, 'Time': 2, 'Steer': -22.0}
        # })
        #
        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': speed, 'Time': 1, 'Steer': -2.8}
        # })
        #
        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': -speed, 'Time': 1, 'Steer': -4.0}
        # })
        #
        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': -22.0}
        # })
        #
        # self.queue_list['Warning'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': speed, 'Time': 1.5, 'Steer': 22.0}
        # })


    def send_stop_sequence(self):
        DataSender.send('/sign', {'sign': 'Stop'})
        # self.queue_list['Critical'].put({
        #     "Owner": Control.Owner.value,
        #     "msgID": Control.msgID.value,
        #     "msgType": Control.msgType.value,
        #     "msgValue": {'Speed': 0, 'Time': 3, 'Steer': 0}
        # })
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

    def send_crosswalk_sequence(self):
        print("############### LOWERING SPEED")
        DataSender.send('/sign', {'sign': 'Crosswalk'})
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
