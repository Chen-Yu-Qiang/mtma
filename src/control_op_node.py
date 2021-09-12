#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import threading
import time
Tello_list=[1,2]

rospy.init_node('control_op_node', anonymous=True)
takeoff_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/takeoff', Empty, queue_size=1) for i in Tello_list]
land_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/land', Empty, queue_size=1) for i in Tello_list]
isSIM=rospy.get_param('isSIM')
while 1:
    print("t=takeoff\nl=land\n>>>")
    op=raw_input()
    if op == "t":
        rospy.loginfo("takeoff!")
        if isSIM==0:
            for i in range(len(takeoff_pub_list)):
                takeoff_pub_list[i].publish(Empty())
                rospy.loginfo("drone"+str(Tello_list[i])+" real takeoff!")
    else:
        rospy.loginfo("land!!!")
        if isSIM==0:
            for i in range(len(land_pub_list)):
                land_pub_list[i].publish(Empty())
                rospy.loginfo("drone"+str(Tello_list[i])+"real land!!!")