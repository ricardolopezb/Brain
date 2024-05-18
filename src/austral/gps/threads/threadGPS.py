# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

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

from src.austral.configs import IS_BLIND, TARGET_COORDINATES
from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (Location, SteerMotor)


class threadGPS(ThreadWithStop):
    """This thread handles the GPS.\n

    Args:

        queueList (dictionary of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
    """

    # ===================================== INIT =========================================
    def __init__(self, queueList, direction_provider):
        super(threadGPS, self).__init__()
        self.queuesList = queueList
        self.Queue_Sending()
        pipeRecvLocation, pipeSendLocation = Pipe(duplex=False)
        self.pipeRecvLocation = pipeRecvLocation
        self.pipeSendLocation = pipeSendLocation
        self.direction_provider = direction_provider
        self.first_time = True
        self.subscribe()

    def subscribe(self):
        """Subscribe function. In this function we make all the required subscribe to process gateway"""
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Location.Owner.value,
                "msgID": Location.msgID.value,
                "To": {
                    "receiver": "threadGPS",
                    "pipe": self.pipeSendLocation,
                },
            }
        )

    # ====================================== RUN ==========================================
    def run(self):
        while self._running:
            if self.first_time:
                self.first_time = False
                # self.direction_provider.set_route((current_x, current_y), TARGET_COORDINATES)
                #self.direction_provider.set_route((0.33, 10.81), TARGET_COORDINATES) # Starting in node 443
                #self.direction_provider.set_route((3.79, 6.88), TARGET_COORDINATES) # Starting in node 150
                continue
            if self.pipeRecvLocation.poll():
                # msg = self.pipeRecvLocation.recv()
                # print("LOCATION MESSAGE RECEIVED:", msg)
                # current_x = msg["x"]
                # current_y = msg["y"]
                # if self.first_time:
                #     self.first_time = False
                #     # self.direction_provider.set_route((current_x, current_y), TARGET_COORDINATES)
                #     self.direction_provider.set_route((0.74, 5.73), TARGET_COORDINATES)
                #     continue
                pass

                #angle_to_steer = self.direction_provider.get_direction(current_x, current_y, IS_BLIND)
                #print("ANGLE TO STEER:", angle_to_steer)
                #self.send_steering(angle_to_steer['steer'])

    def send_steering(self, angle_to_steer):
        self.queuesList['Warning'].put({
            "Owner": SteerMotor.Owner.value,
            "msgID": SteerMotor.msgID.value,
            "msgType": SteerMotor.msgType.value,
            "msgValue": angle_to_steer
        })

    # ==================================== SENDING =======================================
    def Queue_Sending(self):
        pass
