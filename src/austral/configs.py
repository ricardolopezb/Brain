ENABLE_LANE_DETECTION = True
ENABLE_SIGN_DETECTION = True
ENABLE_FRONTAL_ULTRASONIC = True

MODEL_API_URL = "http://192.168.0.102:5000"

# LANES
PID_TOLERANCE = 30
PID_KP = 0.1
PID_KI = 0.05
PID_KD = 0.05

THRESHOLD = 100
KERNEL = 9
ROI = 30
NECESSARY_VOTES = 50

NEW_VOTES_LOGIC_ENABLED = False

def set_new_votes_logic(value):
    global NEW_VOTES_LOGIC_ENABLED
    print("### SETTING NEW VOTES LOGIC TO", value)
    NEW_VOTES_LOGIC_ENABLED = value

# THRESHOLD = 150
# KERNEL = 11
# ROI = 35

BASE_SPEED = 5
#LOW_SPEED = BASE_SPEED / 2
LOW_SPEED = 3

# SIGNS
CROSSWALK_EXECUTION_DURATION = 5
STOP_DURATION = 3
PARKING_SPEED = 15

# FRAMES PARAMS
LANES_FPS = 1
SIGNS_FPS = 3

