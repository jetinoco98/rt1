RESEARCH TRACK 1

ASSIGNMENT 1

Student: Josue Tinoco

================================

This is my personal approach on a simple code that brings all boxes together.

In summary, the robot will initially find the nearest box it sees and use its position as a reference point to gather all other boxes that it later finds. The code of that robot, an id-like number obtained from the vision system, is saved into a list called "Prime Boxes". 
Once it encounters another box (*taking into consideration that if it sees multiple of them it will choose the closest one*) the robot will go to it and grab it. 
Then it will find and go to any "prime box" in the arena, and release next to it the box that its holding. That box's code will be inserted into the "Prime Boxes" list, so that in next iterations the robot can find the closest "prime box" that it sees, and not just the initial box.

All of the above will execute in a controlled loop until all boxes in the arena become "prime boxes". Once that happens, the objective is complete and the program can finish. 

This can be also be expressed in the pseudocode presented below:

**1. Pseudocode for code execution loop.**

    while True:
        if robot_holding_box == True:
            **find_closest_box**
            if elements_in_prime_boxes_list == 0:
                insert_robot_code_in_prime_boxes_list
                move_to_next_iteration
            **go_to_box_and_grab_it**
        **find_prime_box**
        **go_to_prime_box_and_release_grabbed_box**
        drive_backwards

**2. Pseudocode for each of the functions used.**

**2.1 find_closest_box**
    while True:
        i = 1
        codes_of_boxes = []
        distances_of_boxes = []
        see_boxes
        filter_out_boxes_already_in_prime_list
        if box_seen:
            stop_turning
            from element in box list:
                insert_box_code_into_list
                insert_box_distance_into_list
            calculate_closest_box
            obtain_code_of_closest_box
            return code
        else:
            turn_box
            i+=1
            if box_has_turned_360_degrees
                end_program

**2.2 go_to_box_and_grab_it**
    while True:
        obtain_box_data
        go_to_box
        if distance_to_box <= treshold:
            stop_robot
            grab_box
            robot_holding_box = True

**2.2.1 go_to_box**
    if box_rotation_value < -(rotation_treshold):
        turn_counterclockwise
    if if box_rotation_value < rotation_treshold:
        turn_clockwise
    else:
        stop_turning
        drive_robot_forward

**2.3 find_prime_box**
    while True:
        turn_robot
        if prime_box_detected:
            stop_robot
            return prime_box_code

**2.4 go_to_prime_box_and_release_grabbed_box**
    while True:
        obtain_box_data
        go_to_box
        if distance_to_prime_box < release_treshold_value:
            stop_robot
            release_the_box
            robot_holding_box = False
            insert_box_code_into_prime_boxes_list
