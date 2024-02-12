from __future__ import print_function

import time
from sr.robot import *

R = Robot()

#### DECLARATION OF GLOBAL VARIABLES
''' Threshold for the control of the orientation'''
a_th = 2.0
'''Threshold for the control of the linear distance'''
d_th = 0.4
'''An arbitrary maximum speed for the robot'''
max_speed = 100
'''A relative low speed for the robot'''
low_speed = 20
''' A boolean state to show the grab status'''
has_box = False

# New Variables
robot_vision = {}  #  Code: (distance, angle)
total_boxes = []  # All boxes in the window
boxes_at_goal = []  # All boxes that have been placed together

# EXAM EXCLUSIVE VARIABLES
boxes_by_size = []

########################
# FUNCTIONS
########################

def drive(speed, seconds=0):
    """
    Function for setting a linear velocity. 
    If the seconds are 0, the linear velocity will remain.
    If the seconds provided are more than 0, the robot will move for the provided amount of time.
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed

    if abs(seconds) > 0:
        time.sleep(seconds)
        R.motors[0].m0.power = 0
        R.motors[0].m1.power = 0

def turn(speed, seconds=0):
    """
    Function for setting an angular velocity. 
    If the seconds are 0, the angular velocity will remain.
    If the seconds provided are more than 0, the robot will move for the provided amount of time.
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    if seconds > 0:
        time.sleep(seconds)
        R.motors[0].m0.power = 0
        R.motors[0].m1.power = 0

def stop():
    '''Stop the robot. That's it.'''
    drive(0)
    turn(0)

def speed_selector(distance):
    ''' Velocity depends on the distance to the goal box'''
    speed = 0
    if distance > 0.9:
        speed = max_speed
    elif d_th < distance <= 0.9:
        speed = low_speed
    return speed

def update_vision_data():
    global robot_vision
    robot_vision = {}
    markers = [marker for marker in R.see()]
    for m in markers:
        code = m.info.code
        distance = m.dist
        rot = m.rot_y
        robot_vision[code] = [distance, rot]

def initial_scan():
    '''This function will try to scan the data from all the boxes in the arena'''
    boxes_dict = {} # List of the data for all the boxes found
    for i in range(11):
        # Obtaining all markers in the robot's view
        markers = [marker for marker in R.see()]
        # SCAN the environment with 2 sweeps (left and right)
        if i < 4:
            turn(10)
        else:
            turn(-10)
        # We iterate through the markers list and extract all boxes codes and it corresponding distances.
        for m in markers:
            code = m.info.code
            distance = m.dist
            angle = m.rot_y
            if code not in boxes_dict:
                boxes_dict[code] = (distance, angle)
        time.sleep(0.5)
        i+=1
    # After the for loop ends
    stop()
    return boxes_dict

def find_closest_box(codes):
    ''' This function finds the closest box from the robot's vision system.
        If a code list (codes) is given, it will filter the search.'''
    global robot_vision, boxes_at_goal, has_box

    start_time = time.time()
    timeout_seconds = 5

    filtered_robot_vision = {}

    # Loops ends until box is found or timeout is reached.
    while True:
        update_vision_data()
        min_distance = 100
        min_distance_code = None

        # Filter the vision system by the codes provided
        for code in codes:
            if code in robot_vision:
                filtered_robot_vision[code] = robot_vision[code]
        
        # Obtain the box with the minimum distance
        for code, info in filtered_robot_vision.items():
            distance = info[0]
            if distance < min_distance:
                min_distance = distance
                min_distance_code = code

        # If not a single box is found, turn robot and update vision.
        if min_distance_code is None:
            turn(40)
        else:
            stop()
            return min_distance_code
        
        # Exit the program if timout is reached
        if time.time() - start_time > timeout_seconds:
            print("No more boxes found. Program has finished.")
            stop()
            return None

def go_to_box(robot_vision, code):
    '''The go function moves the robot towards the specified box.
        False: The code is not in the robot_vision list
        True: The robot has reached the distance threshold'''
    dist, rot = None, None
    for box, info in robot_vision.items():
        if box == code:
            dist = info[0]
            rot = info[1]
    if dist is None or rot is None or code == 0:
        stop()
        return False

    # If the angle exceeds the threshold, it will reorient itself
    if rot < -a_th:
        turn(-5)
        #print('Changing Rot',dist, rot)
    elif rot > a_th:
        turn(5)
        #print('Changing Rot',dist, rot) 
    # With correct angle, the robot will drive to the box.
    else:
        turn(0)
        speed = speed_selector(dist)
        drive(speed)
        #print('Changing dist',dist, rot)

    time.sleep(0.1)
    if dist <= d_th and not has_box:
        stop()
        return True
    elif dist <= d_th + 0.15 and has_box:
        stop()
        return True

def robot_action():
    global boxes_at_goal, has_box, target_box, last_grabbed_box

    if not has_box:
        R.grab()
        print("The robot has picked up a box. Target box is:", target_box)
        has_box = True
        target_box = 0

    elif has_box:
        R.release()
        print("The robot has released the box")
        boxes_at_goal.append(last_grabbed_box)
        has_box = False
        target_box = 0
        drive(-100, 0.5)

def clasify_boxes(initial_boxes):
    global boxes_by_size

    all_codes = []
    boxes_low = []
    boxes_med = []
    boxes_high = []

    for code in initial_boxes:
        all_codes.append(code)
    n = len(all_codes)
    quantity = int(n/3)
    extra = n % 3

    while len(boxes_low) < quantity:
        code = min(all_codes)
        boxes_low.append(code)
        all_codes.remove(code)

    while len(boxes_med) < quantity:
        code = min(all_codes)
        boxes_med.append(code)
        all_codes.remove(code)
    
    while len(boxes_high) < quantity + extra:
        code = min(all_codes)
        boxes_high.append(code)
        all_codes.remove(code)

    boxes_by_size.append(boxes_low)
    boxes_by_size.append(boxes_med)
    boxes_by_size.append(boxes_high)


########################
# CODE EXECUTION
########################

initial_boxes = initial_scan() # Dict => code:(dist,ang)
print('INITIAL BOXES:', initial_boxes)
print('Number of boxes found:', len(initial_boxes))
clasify_boxes(initial_boxes)
print('Boxes by size:', boxes_by_size)

# Create a list named 'boxes' with the codes of all boxes found during initial scan
for box in initial_boxes:
    total_boxes.append(box)


for boxes in boxes_by_size:
    boxes_at_goal = []
    # Find the initial closest box and set it up as the main box
    main_box = find_closest_box(boxes)
    boxes_at_goal.append(main_box)
    print('The box #', main_box, ' was the closest found, so all boxes will be placed next to it.')

    # Initialization of variables with unexisting box code.
    target_box = 0
    last_grabbed_box = 0


    while True:

        ### Update the info of the boxes currently being seen
        update_vision_data()

        ### Action: Robot to box -> GRAB
        if not(has_box):
            go_status = go_to_box(robot_vision, target_box)

            # The robot has reached a box
            if go_status == True:
                robot_action()

            # The robot cannot see any box
            if go_status == False:
                print('Re-scaning...')
                available_boxes = [x for x in boxes if x not in boxes_at_goal]
                print('Available boxes:', available_boxes)
                if not available_boxes:
                    break
                target_box = find_closest_box(available_boxes)
                if target_box is None:
                    break
                last_grabbed_box = target_box

        ### Action: Robot to box -> RELEASE
        elif (has_box):
            go_status = go_to_box(robot_vision, target_box)

            # The robot has reached a box
            if go_status == True:
                robot_action()

            # The robot cannot see any box
            if go_status == False:
                print('Re-scaning...')
                print('Boxes at goal:', boxes_at_goal)
                target_box = find_closest_box(boxes_at_goal)
                if target_box is None:
                    break

print('Program has finished!')
