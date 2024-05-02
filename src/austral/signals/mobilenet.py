import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util

pkg = importlib.util.find_spec('tflite_runtime')
use_TPU = False
if pkg:
    from tflite_runtime.interpreter import Interpreter

    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter

    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate


class MobilenetSignDetector:
    def __init__(self):
        MODEL_NAME = 'custom_model_lite'
        GRAPH_NAME = 'detect.tflite'
        LABELMAP_NAME = 'labelmap.txt'
        use_TPU = False

        self.input_mean = 127.5
        self.input_std = 127.5

        # Program settings
        self.min_conf_threshold = 0.50
        self.resW, self.resH = 1280, 720  # Resolution to run camera at
        self.imW, self.imH = self.resW, self.resH

        ### Set up model parameters

        # If using Edge TPU, assign filename for Edge TPU model
        if use_TPU:
            # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
            if (GRAPH_NAME == 'detect.tflite'):
                GRAPH_NAME = 'edgetpu.tflite'

        # Get path to current working directory
        CWD_PATH = os.getcwd()

        # Path to .tflite file, which contains the model that is used for object detection
        PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, GRAPH_NAME)

        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH, MODEL_NAME, LABELMAP_NAME)

        # Load the label map
        with open(PATH_TO_LABELS, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

        ### Load Tensorflow Lite model
        # If using Edge TPU, use special load_delegate argument
        if use_TPU:
            self.interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                           experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
        else:
            self.interpreter = Interpreter(model_path=PATH_TO_CKPT)

        self.interpreter.allocate_tensors()

        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.5
        self.input_std = 127.5

        # Check output layer name to determine if this model was created with TF2 or TF1,
        # because outputs are ordered differently for TF2 and TF1 models
        self.outname = self.output_details[0]['name']

        if ('StatefulPartitionedCall' in self.outname):  # This is a TF2 model
            self.boxes_idx, self.classes_idx, self.scores_idx = 1, 3, 0
        else:  # This is a TF1 model
            self.boxes_idx, self.classes_idx, self.scores_idx = 0, 1, 2

    def get_objects(self, frame):
        found_objs = []
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)
        if self.floating_model:
            input_data = (np.float32(input_data) - self.input_mean) / self.input_std
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[self.boxes_idx]['index'])[
            0]  # Bounding box coordinates of detected objects
        classes = self.interpreter.get_tensor(self.output_details[self.classes_idx]['index'])[
            0]  # Class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[self.scores_idx]['index'])[
            0]  # Confidence of detected objects

        for i in range(len(scores)):
            if ((scores[i] > self.min_conf_threshold) and (scores[i] <= 1.0)):
                object_name = self.labels[int(classes[i])]  # Look up object name from "labels" array using class index
                found_objs.append(object_name)

        return found_objs
