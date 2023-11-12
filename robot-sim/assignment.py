from __future__ import print_function

import time
from sr.robot import *

R = Robot()


#### DECLARATION OF GLOBAL VARIABLES

''' Threshold for the control of the orientation'''
a_th = 2.0
'''Threshold for the control of the linear distance'''
d_th = 0.4
'''List of IDs of boxes that have been put together'''
primel = []
'''An arbitrary maximum speed for the robot'''
max_speed = 100
'''A relative low speed for the robot'''
low_speed = 20

grabbed = False

#### FUNCTIONS FOR THE CODE EXECUTION

def drive(speed, seconds):
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

def turn(speed, seconds):
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
    drive(0,0)
    turn(0,0)

def obtain_speed(distance):
    ''' A function so that when the robot reaches the selected distance of 1
    with respect to a box, its velocity will decrease to the low value'''
    # The distance of 0.9 does not represent any special calculated value, but just a treshold chosen by internal testing.
    if distance > 0.9:
        speed = max_speed
    else:
        speed = low_speed
    return speed

def special_turn(i):
    # Robot looks to the near left
    if 0<i<10:
        turn(-50,0.05)
    # Robot looks to the near right
    elif 10<i<30:
        turn(50,0.05)
    # Robot keeps turning clockwise.
    else:
        turn(50,0.1)

def find_closest_box():
    '''As the name suggests, this function is used to find the closest box that the robot is 
        able to see with its integrated vision system (the R.see() function)'''
    codel = []  # List of all the boxes codes found
    distl = []  # List of all distances found
    i = 0
    while 1:
        # Obtaining all markers in the robot's view
        raw_markers = R.see()
        markers = [marker for marker in raw_markers if marker.info.code not in primel]

        #If at least one marker is found, then it should be the closest box.
        if len(markers)>0:
            # In case the code in else was executed first, we should stop the robot from turning.
            turn(0,0)
            # We iterate through the markers list and extract all boxes codes and it corresponding distances.
            for m in markers:
                box_code = m.info.code
                box_distance = m.dist
                codel.append(box_code)
                distl.append(box_distance)

            # The minimum values obtainted from the lists represent the closest found box.
            min_dist = min(distl)
            min_dist_index = distl.index(min_dist)
            code = codel[min_dist_index]

            # The value of the code that represents the closest box will be used for the go_grab function.
            return code
        
        # If the robot cannot see any marker, it will begin to turn.
        else:
            turn(50,0.05)
            # If after a calculated number iterations (robot turns >360°) the robot cannot find any box... 
            # ...it's because they are all grouped together abd the robot's job is complete.
            if i>60:
                turn(0,0)
                print('Could not find any more boxes in the Arena.')
                print('PROGRAM HAS ENDED')
                exit()
            i+=1

def find_prime_box(codel):
    i = 0
    while True:
        # It was discovered that it's not uncommon for the robot to lose vision of the prime box despite being in front.
        # A special series of turning actions was coded inside the special_turn() function.
        special_turn(i)
        markers = R.see()
        for m in markers:
            if m.info.code in codel:
                stop()
                return m.info.code
        i+=1 

def box_data(code):
    '''This function uses the code of the box that the robot must go to, in order to extract the distance and rotation
        values obtained from the robot's vision system (the R.see() function)'''
    while 1:
        try:
            markers = R.see()
            for m in markers:
                if m.info.code == code:
                    box_distance = m.dist
                    box_rot = m.rot_y
            return box_distance, box_rot
        except:
            print('Error in box data while looking for box with code: ', code)
            break

def go(dist,rot):
    '''The go function moves the robot towards the specified box.'''
    # If the angle exceeds the threshold, it will reorient itself
    time.sleep(0.1)
    if rot < -a_th:
        turn(-5, 0)
        print('Changing Rot',dist, rot)
    elif rot > a_th:
        turn(5, 0)
        print('Changing Rot',dist, rot) 
    # Else, it will drive at a certain speed to the box
    else:
        turn(0,0)
        speed = obtain_speed(dist)
        drive(speed,0)
        print('Changing dist',dist, rot)

def go_grab(code):
    global grabbed
    print('Executing the Grab function.')
    while 1:
        dist, rot = box_data(code)
        go(dist,rot)
        if dist <= d_th:
            stop()
            R.grab()
            grabbed = True
            break

def go_release(prime_code, code):
    global grabbed
    print('Executing the Release function')
    while True:
        dist, rot = box_data(prime_code)
        go(dist,rot)
        # The release distance as the value (d_th+0.15) was chosen by preference.
        # It avoids crashing with the boxes but also places them at a reasonable distance amongst themselves.
        if dist <= d_th+0.15:
            stop()
            R.release()
            grabbed = False
            primel.append(code)
            return 0


#### BEGGINING OF CODE EXECUTION LOOP

while True:
    # The moment the program starts the robot will find the closest box it can see.
    if grabbed == False:
        code = find_closest_box()

        # For the first iteration, the closest box found will be added instantly as a prime box.
        # The code of a prime box will be added to a list called 'primel'
        # All boxes grabbed will be put together with any box from the list 
        if len(primel) == 0:
            primel.append(code)
            continue
        
        # After finding the closest box the robot will go to it and grab it.
        try:
            go_grab(code)
        except:
            print('Error in grab function')
            stop()
            # Most likely the R.see() lost sight of the box, so the code can execute again.
            continue
    
    # After grabbing a box the robot will find any prime box where all other boxes will be put together
    prime_code = find_prime_box(primel)

    # After finding any prime box, the robot will go to it and release its box in a specific number of meters next to it.
    try:
        go_release(prime_code, code)
    except:
        print('Error in release function')
        stop()
        # Most likely the R.see() lost sight of the prime box, so the code can execute again.
        continue

    # The robot will go backwards for a few units of distance in order to avoid any collision while looking for next box.
    drive(-100, 0.5)
    print("IDs of boxes brought together: ",primel)

