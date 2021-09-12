#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import time
import os
from std_msgs.msg import Empty
import numpy as np
t=float(0)

is_takeoff=0
def cb_takeoff(data):
    global is_takeoff,t
    is_takeoff=1
    t=float(0)

def land():
    for i in land_pub_list:
        i.publish(Empty())

rospy.init_node('all_ref_node', anonymous=True)




Tello_list=[1,2]
land_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/land', Empty, queue_size=1) for i in Tello_list]
ref_raw_pub_list = [rospy.Publisher("drone"+str(i)+'/ref_bef', Twist, queue_size=1) for i in Tello_list]




takeoff_sub = rospy.Subscriber('/drone1/tello/takeoff', Empty, cb_takeoff)
Ts=1.0/30.0
rate = rospy.Rate(1/Ts)
m=0
times=0
while not rospy.is_shutdown():
    if is_takeoff:
        print(t)
        if m==0:
            if t>=15:
                m=1
                t=float(0)
            else:
                t=t+Ts

                d1_ref_msg=Twist()
                d1_ref_msg.linear.x = 1.5
                d1_ref_msg.linear.y = -0.3
                d1_ref_msg.linear.z = 1.5
                d1_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[0].publish(d1_ref_msg)

                d2_ref_msg=Twist()
                d2_ref_msg.linear.x = 1.5
                d2_ref_msg.linear.y = 0.3
                d2_ref_msg.linear.z = 1.5
                d2_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[1].publish(d2_ref_msg)
        if m==1:
            if t>=15:
                m=2
                t=float(0)
            else:
                t=t+Ts
                d1_ref_msg=Twist()
                d1_ref_msg.linear.x = 1.5+t/10.0
                d1_ref_msg.linear.y = -0.3+t/25.0
                d1_ref_msg.linear.z = 1.5
                d1_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[0].publish(d1_ref_msg)

                d2_ref_msg=Twist()
                d2_ref_msg.linear.x = 1.5
                d2_ref_msg.linear.y = 0.3
                d2_ref_msg.linear.z = 1.5
                d2_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[1].publish(d2_ref_msg)
        if m==2:
            if t>=15:
                m=3
                t=float(0)
            else:
                t=t+Ts
                d1_ref_msg=Twist()
                d1_ref_msg.linear.x = 3
                d1_ref_msg.linear.y = 0.3
                d1_ref_msg.linear.z = 1.5
                d1_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[0].publish(d1_ref_msg)

                d2_ref_msg=Twist()
                d2_ref_msg.linear.x = 1.5+t/10.0
                d2_ref_msg.linear.y = 0.3-t/25.0
                d2_ref_msg.linear.z = 1.5
                d2_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[1].publish(d2_ref_msg)
        if m==3:
            if t>=15:
                m=100
                t=float(0)
            else:
                t=t+Ts
                d1_ref_msg=Twist()
                d1_ref_msg.linear.x = 3
                d1_ref_msg.linear.y = 0.3
                d1_ref_msg.linear.z = 1.5
                d1_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[0].publish(d1_ref_msg)

                d2_ref_msg=Twist()
                d2_ref_msg.linear.x = 3
                d2_ref_msg.linear.y = -0.3
                d2_ref_msg.linear.z = 1.5
                d2_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[1].publish(d2_ref_msg)

        
        if m==100:
            land()
            m=101
    # print(t)
    rate.sleep()
