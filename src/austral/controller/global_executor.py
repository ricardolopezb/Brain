import time

from src.austral.configs import HIGHWAY_ADDITIONAL_SPEED, BASE_SPEED, MODE
from src.utils.messages.allMessages import EnableSignDetection, EnableLaneDetection, EnableSemaphoreDetection, \
    SteerMotor, SpeedMotor


class GlobalExecutor:
    def __init__(self):
        self.has_seen_cruce = False

    def execute(self, queues_list, action):
        if action['name'] == "Curva 1":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
        if action['name'] == "Cruce BUS-MINIAUTOPISTA":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            time.sleep(2)
            self.send_lanes_enablement(queues_list, False)
            if not self.has_seen_cruce:
                self.send_manual_steer(queues_list, 22)
                self.has_seen_cruce = True
            else:
                self.send_manual_steer(queues_list, -3)
                time.sleep(2)


        if action['name'] == "Entrada Rotonda":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])

        if action['name'] == "Reentrada Rotonda":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
        if action['name'] == "Entrada Autopista":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            self.send_manual_speed(queues_list, BASE_SPEED + HIGHWAY_ADDITIONAL_SPEED)
        if action['name'] == "Salida Autopista":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            self.send_manual_speed(queues_list, BASE_SPEED)

        if action['name'] == "Primer Stop":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            time.sleep(2)
            self.send_lanes_enablement(queues_list, False)
            self.send_manual_steer(queues_list, -22)

        if action['name'] == "Entrada SpeedCurve":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            self.send_lanes_enablement(queues_list, True)
            self.send_manual_speed(queues_list, BASE_SPEED + HIGHWAY_ADDITIONAL_SPEED)

        if action['name'] == "Salida SpeedCurve":
            self.send_manual_speed(queues_list, BASE_SPEED)
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            self.send_lanes_enablement(queues_list, False)

        if action['name'] == "Speed Challenge End":
            if MODE == "SPEED":
                print("****** FINISHED SPEED CHALLENGE")
                self.send_manual_speed(queues_list, 0)
            else:
                self.send_lanes_enablement(queues_list, False)
                self.send_manual_steer(queues_list, 22)
                self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
                time.sleep(2)
                self.send_manual_steer(queues_list, -22)

        if action['name'] == "Only Semaphore":
            self.send_semaphores_enablement(queues_list, True)

        if action['name'] == "City Center Exit":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])
            time.sleep(2)
            self.send_manual_steer(queues_list, -22)

        if action['name'] == "Parking Start":
            self.send_sign_enablement(queues_list, True, action['data']['possible_signs'])

        if action['name'] == "Start Position":
            self.send_manual_speed(queues_list, 0)
            self.send_semaphores_enablement(queues_list, True)
        if action['name'] == "Bus Lane Exit":
            if MODE == "REGULAR":
                print("*** END OF RUN")
                self.send_manual_speed(queues_list, 0)

        if action['name'] == "Apaga Signs y prende lanes y apagar semaforo":
            self.send_sign_enablement(queues_list, False, action['data']['possible_signs'])
            self.send_lanes_enablement(queues_list, True)
            self.send_semaphores_enablement(queues_list, False)

    def send_sign_enablement(self, queuesList, enabled, possible_signs):
        queuesList['Critical'].put({
            "Owner": EnableSignDetection.Owner.value,
            "msgID": EnableSignDetection.msgID.value,
            "msgType": EnableSignDetection.msgType.value,
            "msgValue": {'enable': enabled, 'possible_signs': possible_signs}
        })

    def send_lanes_enablement(self, queuesList, enabled):
        queuesList['Critical'].put({
            "Owner": EnableLaneDetection.Owner.value,
            "msgID": EnableLaneDetection.msgID.value,
            "msgType": EnableLaneDetection.msgType.value,
            "msgValue": enabled
        })

    def send_semaphores_enablement(self, queuesList, enabled):
        queuesList['Critical'].put({
            "Owner": EnableSemaphoreDetection.Owner.value,
            "msgID": EnableSemaphoreDetection.msgID.value,
            "msgType": EnableSemaphoreDetection.msgType.value,
            "msgValue": enabled
        })

    def send_manual_steer(self, queuesList, steer_angle):
        queuesList['Critical'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": steer_angle
        })

    def send_manual_speed(self, queuesList, speed):
        queuesList['Critical'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": speed
        })
