import time

from src.austral.configs import BASE_SPEED, PARKING_SPEED, EMPTY_PARKING_PERIOD
from src.utils.messages.allMessages import SpeedMotor, Control, UltrasonicStatusEnqueuing, SteerMotor, \
    ShouldHandleFrontUltrasonic


class ParkingExecutor:

    def __init__(self, pipeRecieveUltrasonics):
        self.pipeRecieveUltrasonics = pipeRecieveUltrasonics
        self.right_sensor_period = EMPTY_PARKING_PERIOD
        self.left_sensor_period = EMPTY_PARKING_PERIOD
        self.starting_empty_right_time = time.time()
        self.starting_empty_left_time = time.time()

    def execute(self, queue_list):
        global allow_ultrasonics_enqueue
        print("### EXECUTING PARKING SEQUENCE ###")
        queue_list['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": -3
        })
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 5
        })
        self.send_enqueue_enablement(queue_list, 'frontal', False)
        self.send_enqueue_enablement(queue_list, 'lateral', True)
        while True:
            if self.pipeRecieveUltrasonics.poll():
                ultrasonics_status = self.pipeRecieveUltrasonics.recv()
                print("DEQUEUING ULTRASONIC IN PARKING", ultrasonics_status)
                if ultrasonics_status['value']['right'] == 1:
                    self.starting_empty_right_time = time.time()
                if ultrasonics_status['value']['left'] == 1:
                    self.starting_empty_left_time = time.time()
                current_time = time.time()
                if ultrasonics_status['value']['right'] == 0:
                    if current_time - self.starting_empty_right_time > self.right_sensor_period:
                        print("PARKING ON THE RIGHT")
                        self.send_enqueue_enablement(queue_list, 'lateral', False)
                        self.send_parking_sequence(queue_list, 'right')  # parking derecho
                        break

                if ultrasonics_status['value']['left'] == 0:
                    if current_time - self.starting_empty_left_time > self.left_sensor_period:
                        print("PARKING ON THE LEFT")
                        self.send_enqueue_enablement(queue_list, 'lateral', False)
                        self.send_parking_sequence(queue_list, 'left')  # parking izquierdo
                        break

    def send_parking_sequence(self, queue_list, side):
        multiplier = 1
        if side == 'left':
            multiplier = -1
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
        time.sleep(8)
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
            "msgValue": {'Speed': -speed, 'Time': 4, 'Steer': 23.0 * multiplier}
        })
        time.sleep(4)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 4, 'Steer': -23.0 * multiplier}
        })
        time.sleep(4)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 1, 'Steer': 10 * multiplier}
        })
        time.sleep(1)
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        time.sleep(8)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': -speed, 'Time': 1, 'Steer': -3.5}
        })
        time.sleep(1)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 2.5, 'Steer': -22.0 * multiplier}
        })
        time.sleep(2.5)
        queue_list['Critical'].put({
            "Owner": Control.Owner.value,
            "msgID": Control.msgID.value,
            "msgType": Control.msgType.value,
            "msgValue": {'Speed': speed, 'Time': 2.5, 'Steer': 22.0 * multiplier}
        })
        time.sleep(2.5)
        queue_list['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
        self.send_enqueue_enablement(queue_list, 'frontal', True)

    def send_enqueue_enablement(self, queue_list, position, value):
        print(f"** ENQUEUING {position} ENABLEMENT WITH", value)
        if position == 'lateral':
            queue_list['Critical'].put({
                "Owner": UltrasonicStatusEnqueuing.Owner.value,
                "msgID": UltrasonicStatusEnqueuing.msgID.value,
                "msgType": UltrasonicStatusEnqueuing.msgType.value,
                "msgValue": {'value': value}
            })
        if position == 'frontal':
            queue_list['Critical'].put({
                "Owner": ShouldHandleFrontUltrasonic.Owner.value,
                "msgID": ShouldHandleFrontUltrasonic.msgID.value,
                "msgType": ShouldHandleFrontUltrasonic.msgType.value,
                "msgValue": {'value': value}
            })


