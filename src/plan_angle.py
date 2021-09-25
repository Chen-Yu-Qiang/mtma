#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import threading
import mulitTarget
import time
import filter_lib
import kf_lib
import viewPanning
import numpy as np


dt=1.0/30.0


class uav:
    def __init__(self,i):
        self.sub_local_res=rospy.Subscriber("/drone"+str(i)+'/ref_l', Twist, self.opt_ang)
        self.i=i
        self.str_name="drone"+str(i)
        self.vper=viewPanning.viewPanner_angle()
        self.vper.myName=self.str_name
        self.res=Twist()
        self.ci_pub=rospy.Publisher("/drone"+str(i)+'/ref_plan_ang', Twist, queue_size=1)
        self.t=time.time()


    def set_ci(self,_ci):
        self.vper.ci=viewPanning.twist2ci(_ci)

    def opt_ang(self,data):
        self.set_ci(data)
        self.t=time.time()
        self.res=viewPanning.ci2twist(self.vper.opt_ang())
        out_msg=Twist()
        out_msg.linear.x=data.linear.x
        out_msg.linear.y=data.linear.y
        out_msg.linear.z=data.linear.z
        out_msg.angular.z=self.res.angular.z
        self.ci_pub.publish(out_msg)



rospy.init_node('plan_angle_node', anonymous=True)


Tello_list=[1,2]
uav_set=[uav(i) for i in Tello_list]
rospy.spin()