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
import time

from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (
    SteerMotor, EnableButton
)


class threadMock(ThreadWithStop):
    """This thread periodically send a steering order.\n

    Args:
        f_serialCon (serial.Serial): Serial connection between the two boards.
        f_logFile (FileHandler): The path to the history file where you can find the logs from the connection.
        queueList (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
    """

    # ===================================== INIT =========================================
    def __init__(self, queueList):
        print("**** STARTING MOCK THREAD ****")
        super(threadMock, self).__init__()
        self.queuesList = queueList
        self.sent_steering = 10
        self.Queue_Sending()

    # ====================================== RUN ==========================================
    def run(self):
        while True:
            time.sleep(3)
            self.sendqueue()



    # ==================================== SENDING =======================================
    def Queue_Sending(self):
        """Callback function for enable button flag."""
        self.queuesList[EnableButton.Queue.value].put(
            {
                "Owner": EnableButton.Owner.value,
                "msgID": EnableButton.msgID.value,
                "msgType": EnableButton.msgType.value,
                "msgValue": True,
            }
        )
        threading.Timer(1, self.Queue_Sending).start()

    def sendqueue(self):
        print("**** MOCK THREAD SENDING ****", self.sent_steering)
        self.queuesList['General'].put({
            "Owner": SteerMotor.Owner,
            "msgID": SteerMotor.msgID,
            "msgType": SteerMotor.msgType,
            "msgValue": self.sent_steering,
        })
        self.sent_steering = self.sent_steering*(-1)