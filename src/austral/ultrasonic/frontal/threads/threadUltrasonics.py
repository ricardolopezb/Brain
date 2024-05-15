# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.
import json
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
import threading
from multiprocessing import Pipe

from src.austral.api.data_sender import DataSender
from src.austral.configs import BASE_SPEED, allow_ultrasonics_enqueue
from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (
    BatteryLvl,
    ImuData,
    InstantConsumption,
    EnableButton, SpeedMotor, UltrasonicStatus, UltrasonicStatusEnqueuing,
)


class threadUltrasonics(ThreadWithStop):
    """This thread read the data that Arduino Ultrasonic send to Raspberry PI.\n

    Args:
        f_serialCon (serial.Serial): Serial connection between the two boards.
        queueList (dictionary of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
    """

    # ===================================== INIT =========================================
    def __init__(self, f_serialCon, queueList):
        super(threadUltrasonics, self).__init__()
        self.serialCon = f_serialCon
        pipeRecvEnqueueEnablement, pipeSendEnqueueEnablement = Pipe(duplex=False)
        self.pipeRecvEnqueueEnablement = pipeRecvEnqueueEnablement
        self.pipeSendEnqueueEnablement = pipeSendEnqueueEnablement
        self.buff = ""
        self.isResponse = False
        self.queuesList = queueList
        self.acumulator = 0
        self.is_braked = False
        self.should_enqueue = False
        self.should_brake = False
        self.subscribe()

    def subscribe(self):
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": UltrasonicStatusEnqueuing.Owner.value,
                "msgID": UltrasonicStatusEnqueuing.msgID.value,
                "To": {"receiver": "threadUltrasonic", "pipe": self.pipeSendEnqueueEnablement},
            }
        )

    # ====================================== RUN ==========================================
    def run(self):
        while self._running:
            ultrasonics_status = self.read_ultrasonics_state()
            try:
                if ultrasonics_status is None:
                    continue
                self.handle_frontal(ultrasonics_status['front'])
                if self.pipeRecvEnqueueEnablement.poll():
                    self.should_enqueue = self.pipeRecvEnqueueEnablement.recv()['value']['value'] #xd
                    print("RECEIVED ENABLEMENT IN ULTRASONIC WITH VALUE", self.should_enqueue)
                if self.should_enqueue:
                    self.handle_laterals(ultrasonics_status)

            except UnicodeDecodeError:
                pass

    # ==================================== SENDING =======================================

    def handle_frontal(self, read_chr):
        print("ENTERED FRONTAL:", read_chr)
        if read_chr == 0:
            self.should_brake = False
        elif read_chr == 1:
            self.should_brake = True
        else:
            return

        if self.should_brake and not self.is_braked:
            print("*** FRONTAL DETECTED, BRAKING")
            self.brake()
            self.is_braked = True
        if not self.should_brake and self.is_braked:
            print("*** FRONTAL REMOVED, ACCELERATING")
            self.accelerate()
            self.is_braked = False

    def read_ultrasonics_state(self):
        try:
            line = self.serialCon.readline().decode('utf-8').strip()
            if line:
                return json.loads(line)
        except Exception as e:
            print(e)
            return None

    def brake(self):
        print("BRAKING")
        self.queuesList[SpeedMotor.Queue.value].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": 0
        })
        # DataSender.send('/brake', {'braking': True})

    def accelerate(self):
        print("NOTHING IN THE WAY. SPEEDING")
        self.queuesList[SpeedMotor.Queue.value].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })
        # DataSender.send('/brake', {'braking': False})
        # DataSender.send('/speed', {'speed': BASE_SPEED})

    def handle_laterals(self, ultrasonic_status):
        print("SHOULD ENQ?", self.should_enqueue)
        if self.should_enqueue:
            print("ENQUEUING ULTRASONIC")
            self.queuesList[UltrasonicStatus.Queue.value].put({
                "Owner": UltrasonicStatus.Owner.value,
                "msgID": UltrasonicStatus.msgID.value,
                "msgType": UltrasonicStatus.msgType.value,
                "msgValue": ultrasonic_status
            })
