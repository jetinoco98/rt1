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

1. Pseudocode for code execution loop.

while True:


2. Pseudocode for each of the functions used.