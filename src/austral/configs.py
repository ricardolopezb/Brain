import sys

ENABLE_LANE_DETECTION = False
ENABLE_SIGN_DETECTION = False
ENABLE_FRONTAL_ULTRASONIC = False
ENABLE_IMAGE_CAPTURE = False
ENABLE_V2X = True
ENABLE_GPS = True

MODE = "REGULAR"

if len(sys.argv) > 1:
    mode_arg = sys.argv[1]
    if mode_arg == "speed" or mode_arg == "SPEED" or mode_arg == "fast" or mode_arg == "FAST":
        MODE = "SPEED"

if MODE == "SPEED":
    ENABLE_FRONTAL_ULTRASONIC = False
    ENABLE_V2X = False
    ENABLE_GPS = False  # To be defined






# OLD SPEEDS
# BASE_SPEED = 5
# LOW_SPEED = 3


BASE_SPEED = 10
LOW_SPEED = 6
HIGH_SPEED = 30

IS_BLIND = False
MY_CAR_ID = 0
EMPTY_PARKING_PERIOD = 8

allow_ultrasonics_enqueue = False


def set_allow_ultrasonics_enqueue(value):
    global allow_ultrasonics_enqueue
    print("** changing ultrasonic enq allowance value to", value)
    allow_ultrasonics_enqueue = value


V2X_SEMAPHORE_INFLUENCE_RADIUS = 3
V2X_SEMAPHORE_COOLDOWN = 2

USE_DEMO_ROUTE = False
TARGET_COORDINATES = (3.79, 6.88)  # Node 150
# TARGET_COORDINATES = (7.03, 0.89) # Node 223

MODEL_API_URL = "http://192.168.0.100:5000"

# LANES
PID_TOLERANCE = 50
PID_KP = 0.075
PROP_CONSTANT = 1.2

THRESHOLD = 165
KERNEL = 3
ROI = 35

PID_KI = 0.05
PID_KD = 0.05

# THRESHOLD = 100
# KERNEL = 9
# ROI = 30
NECESSARY_VOTES = 50

NEW_VOTES_LOGIC_ENABLED = False

IS_ABLE_TO_PARK = False


def set_parking_ability(value):
    global IS_ABLE_TO_PARK
    IS_ABLE_TO_PARK = value


def set_new_votes_logic(value):
    global NEW_VOTES_LOGIC_ENABLED
    NEW_VOTES_LOGIC_ENABLED = value


def get_new_votes_logic():
    return NEW_VOTES_LOGIC_ENABLED


# SIGNS
CROSSWALK_EXECUTION_DURATION = 5
STOP_DURATION = 3
PARKING_SPEED = 15

# FRAMES PARAMS
LANES_FPS = 1
SIGNS_FPS = 3

DATASET_IMAGE_PERIOD = 2
