#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import time
import os
from std_msgs.msg import Empty
import numpy as np

t=float(0)
Tello_list=[1,2]
is_takeoff=0
def cb_takeoff(data):
    global is_takeoff,t
    is_takeoff=1
    t=float(0)
def land():
    for i in land_pub_list:
        i.publish(Empty())
class plan_res:
    def __init__(self,i):
        self.sub=rospy.Subscriber("drone"+str(i)+'/ref_bef_pre', Twist, self.cb)
        self.d=Twist()
    def cb(self,data):
        self.d=data



rospy.init_node('out_ref_node', anonymous=True)




land_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/land', Empty, queue_size=1) for i in Tello_list]
ref_raw_pub_list = [rospy.Publisher("drone"+str(i)+'/ref_bef', Twist, queue_size=1) for i in Tello_list]
takeoff_sub = rospy.Subscriber('/drone1/tello/takeoff', Empty, cb_takeoff)
plan_res_list=[plan_res(i) for i in Tello_list]
Ts=0.03
rate = rospy.Rate(1/Ts)
m=0
times=0
while not rospy.is_shutdown():
    if is_takeoff:
        # print(t)
        if m==0:
            if t>5:
                m=1
                t=float(0)
            else:
                t=t+Ts

                d1_ref_msg=Twist()
                d1_ref_msg.linear.x = 3.3
                d1_ref_msg.linear.y = -1
                d1_ref_msg.linear.z = 1.2
                d1_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[0].publish(d1_ref_msg)

                d2_ref_msg=Twist()
                d2_ref_msg.linear.x = 3.3
                d2_ref_msg.linear.y = 1
                d2_ref_msg.linear.z = 1.2
                d2_ref_msg.angular.z = 90.0/57.296
                ref_raw_pub_list[1].publish(d2_ref_msg)
        if m==1:
            if t>=65:
                m=100
                t=float(0)
            else:
                t=t+Ts

                ref_raw_pub_list[0].publish(plan_res_list[0].d)

                ref_raw_pub_list[1].publish(plan_res_list[1].d)

        
        if m==100:
            land()
            m=101
    # print(t)
    rate.sleep()
