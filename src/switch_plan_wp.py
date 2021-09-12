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

class a_plan_res:
    def __init__(self,_name):
        self.str_name=_name
        self.sub_res=rospy.Subscriber('plan_wp_'+self.str_name, Twist,self.cb_res)
        self.sub_tpk=rospy.Subscriber('plan_tpk_'+self.str_name, Float32MultiArray,self.cb_tpk)
        self.res=Twist()
        self.tpk=None
        self.is_ok=1

        self.in_num=[51,52]
        self.in_num_obj=None
        self.ang_x=0
    def cb_res(self,data):
        # print(data)
        data.linear.z=data.linear.z+0.5
        self.res=data


    def cb_tpk(self,data):
        self.tpk=data.data
        # print(data)
        if max(self.tpk)>=1 or min(self.tpk)<=-1:
            print(self.ang_x,"out")
            self.is_ok=0
        else:
            self.is_ok=1

    def which_board_timeout(self):
        for i in range(len(self.in_num_obj)):
            if self.in_num_obj[i].istimeout():
                return i
        return -1

    def which_board_timeoutout(self):
        for i in range(len(self.in_num_obj)):
            if self.in_num_obj[i].istimeoutout():
                return i
        return -1

    def get_output_msg(self):
        output_msg=Twist()

        if self.is_ok:
            if self.which_board_timeout()==-1:
                output_msg=self.res

                output_msg.angular.x=self.ang_x
            elif self.which_board_timeoutout()==-1:
                output_msg=self.in_num_obj[self.which_board_timeoutout()].last_see_uav_pos
                output_msg.angular.x=0  
                print("Lost target")                
            else:
                output_msg=self.in_num_obj[self.which_board_timeout()].last_see_uav_pos
                output_msg.angular.x=0  

            return output_msg

class a_board:
    def __init__(self,_num):
        self.sub_res=rospy.Subscriber('target'+str(_num)+"_f", Twist,self.cb_b)
        self.data=Twist()
        self.last_see_time=time.time()
        self.last_see_uav_pos=Twist()
        self.uav_pos=Twist()

    def cb_b(self,_data):
        self.data=_data
        self.last_see_uav_pos=self.uav_pos
        self.last_see_time=time.time()

    def istimeout(self):
        if time.time()-self.last_see_time>100:
            return 1
        else:
            return 0
    def istimeoutout(self):
        if time.time()-self.last_see_time>300:
            return 1
        else:
            return 0


board_set=[a_board(i) for i in [0,51,52]]

def cb_uav(data):
    global board_set
    for i in board_set:
        i.uav_pos=data

rospy.init_node('sw_plan_node', anonymous=True)


def land():
    for i in land_pub_list:
        i.publish(Empty())


Tello_list=[1,2]
land_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/land', Empty, queue_size=1) for i in Tello_list]


pr5152=a_plan_res("51_52_future")
pr5152.in_num_obj=[board_set[1],board_set[2]]
pr5152.in_num=[51,52]
pr5152.ang_x=6

pr52=a_plan_res("52_future")
pr52.in_num_obj=[board_set[2]]
pr52.in_num=[52]
pr52.ang_x=4
rate = rospy.Rate(30)
p5152_pub=rospy.Publisher('ref_bef', Twist, queue_size=1)

#  51+52=110(2)=6(10)
#  52   =100(2)=4(10)
#  51   =010(2)=2(10)
is51or52_pub=rospy.Publisher('is51or52_pub', Twist, queue_size=1)
uav_sub=rospy.Subscriber('from_kf', Twist, cb_uav)
# land_pub = rospy.Publisher('tello/land', Empty, queue_size=1)

takeoff_sub = rospy.Subscriber('/drone1/tello/takeoff', Empty, cb_takeoff)
Ts=0.03
rate = rospy.Rate(1/Ts)
m=0
times=0
while not rospy.is_shutdown():
    if is_takeoff:
        print(t)
        if m==0:
            if t>=5:
                m=1
                t=float(0)
            else:
                t=t+Ts
                ref_pub_msg=Twist()
                ref_pub_msg.linear.x = 1.5
                ref_pub_msg.linear.y = 0
                ref_pub_msg.linear.z = 1.5
                ref_pub_msg.angular.z = 90.0/57.296
                p5152_pub.publish(ref_pub_msg)
        if m==1:
            if t>=5:
                m=2
                t=float(0)
            else:
                t=t+Ts
                ref_pub_msg=Twist()
                ref_pub_msg.linear.x = 2
                ref_pub_msg.linear.y = 0
                ref_pub_msg.linear.z = 1.5
                ref_pub_msg.angular.z = 90.0/57.296
                p5152_pub.publish(ref_pub_msg)
        if m==2:
            if t>=5:
                m=3
                t=float(0)
            else:
                t=t+Ts
                ref_pub_msg=Twist()
                ref_pub_msg.linear.x = 2.5
                ref_pub_msg.linear.y = 0
                ref_pub_msg.linear.z = 1.5
                ref_pub_msg.angular.z = 90.0/57.296
                p5152_pub.publish(ref_pub_msg)
        if m==3:
            if t>=5:
                m=4
                t=float(0)
            else:
                t=t+Ts
                ref_pub_msg=Twist()
                ref_pub_msg.linear.x = 3
                ref_pub_msg.linear.y = 0
                ref_pub_msg.linear.z = 1.5
                ref_pub_msg.angular.z = 90.0/57.296
                p5152_pub.publish(ref_pub_msg)
        if m==4:
            if t>=5:
                m=5
                t=float(0)
            else:
                t=t+Ts
                ref_pub_msg=Twist()
                ref_pub_msg.linear.x = 3.5
                ref_pub_msg.linear.y = 0
                ref_pub_msg.linear.z = 1.5
                ref_pub_msg.angular.z = 90.0/57.296
                p5152_pub.publish(ref_pub_msg)
        if m==5:
            if t>=5:
                m=6
                t=float(0)
            else:
                t=t+Ts
                ref_pub_msg=Twist()
                ref_pub_msg.linear.x = 3.7
                ref_pub_msg.linear.y = 0
                ref_pub_msg.linear.z = 1.5
                ref_pub_msg.angular.z = 90.0/57.296
                p5152_pub.publish(ref_pub_msg)
        if m==6:
            if t>=100:
                m=100
                t=float(0)
            else:
                t=t+Ts
                if pr5152.is_ok:
                    p5152_pub.publish(pr5152.get_output_msg())
                        
                else:
                    p5152_pub.publish(pr52.get_output_msg())
        
        if m==100:
            land()
            m=101
    # print(t)
    rate.sleep()
