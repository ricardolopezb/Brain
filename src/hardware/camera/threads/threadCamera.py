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
import cv2
import threading
import base64
import picamera2
import time

from multiprocessing import Pipe

from src.austral.api.data_sender import DataSender
from src.austral.configs import LANES_FPS, SIGNS_FPS, ENABLE_SIGN_DETECTION, ENABLE_LANE_DETECTION
from src.austral.pid.marcos_lane_detector import MarcosLaneDetector
from src.austral.pid.obj_test import LaneDetector
from src.austral.pid.old_lanes_algoritm import OldLaneDetector
from src.austral.signals.color_detector import ColorDetector
from src.austral.signals.model_detector import ModelDetector
from src.austral.signals.model_request_sender import ModelRequestSender
from src.austral.signals.sign_detector import SignDetector
from src.austral.signals.sign_executor import SignExecutor
from src.utils.messages.allMessages import (
    mainCamera,
    serialCamera,
    Recording,
    Record,
    Config,
    SteeringCalculation
)
from src.templates.threadwithstop import ThreadWithStop

camera_resolution = (512, 270)


class threadCamera(ThreadWithStop):
    """Thread which will handle camera functionalities.\n
    Args:
        pipeRecv (multiprocessing.queues.Pipe): A pipe where we can receive configs for camera. We will read from this pipe.
        pipeSend (multiprocessing.queues.Pipe): A pipe where we can write configs for camera. Process Gateway will write on this pipe.
        queuesList (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
        logger (logging object): Made for debugging.
        debugger (bool): A flag for debugging.
    """

    # ================================ INIT ===============================================
    def __init__(self, pipeRecv, pipeSend, queuesList, logger, debugger):
        super(threadCamera, self).__init__()
        self.queuesList = queuesList
        self.logger = logger
        self.pipeRecvConfig = pipeRecv
        self.pipeSendConfig = pipeSend
        self.debugger = debugger
        self.frame_rate = 5
        self.recording = False
        pipeRecvRecord, pipeSendRecord = Pipe(duplex=False)
        self.pipeRecvRecord = pipeRecvRecord
        self.pipeSendRecord = pipeSendRecord
        self.video_writer = ""
        self.subscribe()
        self._init_camera()
        self.Queue_Sending()
        self.Configs()
        self.lane_detector = MarcosLaneDetector(queuesList)
        # self.sign_detector = ModelDetector()
        self.model_service = ModelRequestSender()
        self.sign_executor = SignExecutor(queuesList)
        self.color_detector = ColorDetector()

        # Variables for run() timing
        self.last_epoch_demo = time.time()
        self.last_epoch_lanes = time.time()
        self.last_epoch_signs = time.time()

        # Cada cuanto quiero que se corra la conditional branch
        self.demo_period = 0.001  # in seconds
        self.lanes_period = 1 / LANES_FPS  # in seconds
        self.signs_period = 1 / SIGNS_FPS  # in seconds

        self.frame = None
        self.last_sent_steering_value = -1000

    def subscribe(self):
        """Subscribe function. In this function we make all the required subscribe to process gateway"""
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Record.Owner.value,
                "msgID": Record.msgID.value,
                "To": {"receiver": "threadCamera", "pipe": self.pipeSendRecord},
            }
        )
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Config.Owner.value,
                "msgID": Config.msgID.value,
                "To": {"receiver": "threadCamera", "pipe": self.pipeSendConfig},
            }
        )

    def Queue_Sending(self):
        """Callback function for recording flag."""
        self.queuesList[Recording.Queue.value].put(
            {
                "Owner": Recording.Owner.value,
                "msgID": Recording.msgID.value,
                "msgType": Recording.msgType.value,
                "msgValue": self.recording,
            }
        )
        threading.Timer(1, self.Queue_Sending).start()

    # =============================== STOP ================================================
    def stop(self):
        if self.recording:
            self.video_writer.release()
        super(threadCamera, self).stop()

    # =============================== CONFIG ==============================================
    def Configs(self):
        """Callback function for receiving configs on the pipe."""
        while self.pipeRecvConfig.poll():
            message = self.pipeRecvConfig.recv()
            message = message["value"]
            print(message)
            self.camera.set_controls(
                {
                    "AeEnable": False,
                    "AwbEnable": False,
                    message["action"]: float(message["value"]),
                }
            )
        threading.Timer(1, self.Configs).start()

    # ================================ RUN ================================================
    def run(self):
        """This function will run while the running flag is True. It captures the image from camera and make the required modifies and then it send the data to process gateway."""
        var = True
        while self._running:
            try:
                if self.pipeRecvRecord.poll():
                    msg = self.pipeRecvRecord.recv()
                    self.recording = msg["value"]
                    if msg["value"] == False:
                        self.video_writer.release()
                    else:
                        fourcc = cv2.VideoWriter_fourcc(
                            *"MJPG"
                        )  # You can choose different codecs, e.g., 'MJPG', 'XVID', 'H264', etc.
                        self.video_writer = cv2.VideoWriter(
                            "output_video" + str(time.time()) + ".avi",
                            fourcc,
                            self.frame_rate,
                            (camera_resolution[0], camera_resolution[1]),
                        )
            except Exception as e:
                print(e)
            if self.debugger == True:
                self.logger.warning("getting image")
            request = self.camera.capture_array("main")
            # request = cv2.cvtColor(request, cv2.COLOR_RGB2BGR)
            if var:
                if self.recording == True:
                    cv2_image = cv2.cvtColor(request, cv2.COLOR_RGB2BGR)
                    self.video_writer.write(cv2_image)

                current_epoch = int(time.time())
                # if current_epoch - self.last_epoch_demo > self.demo_period:
                self.last_epoch_demo = self.last_epoch_demo + self.demo_period

                # if request is None:
                #     var = not var
                #     continue

                if ENABLE_SIGN_DETECTION:
                    _, signs_encoded_img = cv2.imencode(".jpg", request)
                    self.detect_signs(current_epoch, request, signs_encoded_img)

                if ENABLE_LANE_DETECTION:
                    self.detect_lanes(current_epoch, request)

                request2 = self.camera.capture_array(
                    "lores"
                )  # Will capture an array that can be used by OpenCV library
                request2 = request2[:360, :]

                _, encoded_img = cv2.imencode(".jpg", request)
                _, encoded_big_img = cv2.imencode(".jpg", request)
                image_data_encoded = base64.b64encode(encoded_img).decode("utf-8")
                image_data_encoded2 = base64.b64encode(encoded_big_img).decode("utf-8")

                self.queuesList[mainCamera.Queue.value].put(
                    {
                        "Owner": mainCamera.Owner.value,
                        "msgID": mainCamera.msgID.value,
                        "msgType": mainCamera.msgType.value,
                        "msgValue": image_data_encoded2,
                    }
                )
                self.queuesList[serialCamera.Queue.value].put(
                    {
                        "Owner": serialCamera.Owner.value,
                        "msgID": serialCamera.msgID.value,
                        "msgType": serialCamera.msgType.value,
                        "msgValue": image_data_encoded,
                    }
                )

            var = not var

    def detect_lanes(self, current_epoch, request):
        if current_epoch - self.last_epoch_lanes > self.lanes_period:
            self.last_epoch_lanes = self.last_epoch_lanes + self.lanes_period
            steering_value = self.lane_detector.get_steering_angle(request)
            self.send_steering_value(steering_value)

    def detect_signs(self, current_epoch, request, encoded_img):
        if current_epoch - self.last_epoch_signs > self.signs_period:
            self.last_epoch_signs = self.last_epoch_signs + self.signs_period
            mask_frame, found_color = self.color_detector.detect_color(request)

            # LO VOY A HACER AL REVES, DESPUES VEO. CAMBIO LOS COLORES EN EL IF

            if found_color == 'AZUL':
                # self.sign_detector.detect(request, 'stop')
                response = self.model_service.send(encoded_img, 'stop')
                if response['found'] == 'none':
                    return request
                if response['found'] == 'stop':
                    print("###### FOUND A STOP")
                    DataSender.send('/sign', {'sign': 'Stop'})
                    self.sign_executor.execute('stop')

            elif found_color == 'ROJO':
                # self.sign_detector.detect(request, 'crosswalk')

                response = self.model_service.send(encoded_img, 'crosswalk')
                if response['found'] == 'none':
                    return request

                if response['found'] == 'crosswalk':
                    print("###### FOUND A CROSSWALK")
                    DataSender.send('/sign', {'sign': 'Crosswalk'})
                    self.sign_executor.execute('crosswalk')
                else:
                    print("###### FOUND A PARKING")
                    DataSender.send('/sign', {'sign': 'Parking'})
                    self.sign_executor.execute('parking')
            else:
                DataSender.send('/sign', {'sign': None})
                self.sign_executor.execute(None)
            return mask_frame
        return request
        # found_sign = self.sign_detector.detect_signal(request, threshold=10)
        # print(f"************* Found sign: {found_sign}")
        # self.sign_executor.execute(found_sign)

    # =============================== START ===============================================
    def start(self):
        super(threadCamera, self).start()

    # ================================ INIT CAMERA ========================================
    def _init_camera(self):
        """This function will initialize the camera object. It will make this camera object have two chanels "lore" and "main"."""
        self.camera = picamera2.Picamera2()
        config = self.camera.create_preview_configuration(
            buffer_count=1,
            queue=False,
            main={"format": "XBGR8888", "size": (camera_resolution[0], camera_resolution[1])},
            lores={"size": (240, 180)},
            encode="lores",
        )
        self.camera.configure(config)
        self.camera.start()

    def send_steering_value(self, steering_value):
        if self.last_sent_steering_value == steering_value:
            return
        print(f"****** ${time.time()} ********** ENQUEUING STEERING VALUE ${steering_value} ****************")
        self.queuesList[SteeringCalculation.Queue.value].put(
            {
                "Owner": SteeringCalculation.Owner.value,
                "msgID": SteeringCalculation.msgID.value,
                "msgType": SteeringCalculation.msgType.value,
                "msgValue": {'value': steering_value},
            }
        )
        self.last_sent_steering_value = steering_value
