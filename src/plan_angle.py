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

class target:
    def __init__(self,_i):
        self.sub = rospy.Subscriber('/target'+str(_i)+"_f", Twist, self.cb_fun)
        self.sub2 = rospy.Subscriber('/target'+str(_i)+"_f_future", Twist, self.cb_fun2)
        self.i=_i
        self.data=None
        self.future=Twist()
        self.t=time.time()
    def cb_fun(self,_data):
        self.data=_data
        self.t=time.time()
    def cb_fun2(self,_data):
        self.future=_data
    def isTimeout(self):
        if (time.time()-self.t<50) and (not (self.data is None)):
            return 0
        else:
            return 1

target_set=[target(i) for i in range(51,60)]


class uav:
    def __init__(self,i):
        self.sub_local_res=rospy.Subscriber("ref_l", Twist, self.opt_ang)
        self.sub_tracking_num=rospy.Subscriber("tracking_num", Twist, self.cb_tracking_num)
        self.i=i
        self.str_name="drone"+str(i)
        self.vper=viewPanning.viewPanner_angle()
        self.vper.myName=self.str_name
        self.res=Twist()
        self.ci_pub=rospy.Publisher('ref_plan_ang', Twist, queue_size=1)
        self.tpk_bef_pub=rospy.Publisher('plan_tpk_before', Float32MultiArray, queue_size=1)
        self.tpk_aft_pub=rospy.Publisher('plan_tpk_after', Float32MultiArray, queue_size=1)
        self.t=time.time()
        self.tracking_num=0

    def pub_tpk_aft(self):
        d=self.vper.get_tpk()
        dd=Float32MultiArray(data=d)
        self.tpk_aft_pub.publish(dd)
        
    def pub_tpk_bef(self):
        d=self.vper.get_tpk()
        dd=Float32MultiArray(data=d)
        self.tpk_bef_pub.publish(dd)


    def cb_tracking_num(self,data):
        self.tracking_num=data.linear.x
        self.set_tracking_num2taskpoint()

    def set_tracking_num2taskpoint(self):
        global target_set
        if self.tracking_num==2:
            taskPoint=viewPanning.twist2taskpoint([target_set[0].data,target_set[0].future])
            taskPoint=viewPanning.board_Expand(taskPoint)
            self.vper.set_taskPoint(taskPoint)
        if self.tracking_num==4:
            taskPoint=viewPanning.twist2taskpoint([target_set[1].data,target_set[1].future])
            taskPoint=viewPanning.board_Expand(taskPoint)
            self.vper.set_taskPoint(taskPoint)

    def set_ci(self,_ci):
        self.vper.ci=viewPanning.twist2ci(_ci)

    def opt_ang(self,data):
        self.set_ci(data)
        print("bef",self.vper.ci)
        self.t=time.time()
        self.pub_tpk_bef()
        self.res=viewPanning.ci2twist(self.vper.opt_ang())
        self.pub_tpk_aft()
        print("aft",self.vper.ci)
        out_msg=Twist()
        out_msg.linear.x=data.linear.x
        out_msg.linear.y=data.linear.y
        out_msg.linear.z=data.linear.z
        out_msg.angular.z=self.res.angular.z
        self.ci_pub.publish(out_msg)


rospy.init_node('plan_angle_node', anonymous=True)

# Tello_list=[1,2]
# uav_set=[uav(i) for i in Tello_list]

uav(0)

rospy.spin()