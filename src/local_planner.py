#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import time
import numpy as np
from std_msgs.msg import Float32
import filter_lib

box_x=0
box_y=0
box_z=1
box_ang=90
box_newTime=time.time()
is_takeoff=1
l_flag=0
my_data=Twist()
def cb_box(data):
    global my_data
    my_data=data

def cb_takeoff(data):
    global is_takeoff
    time.sleep(5)
    is_takeoff=1

def cb_land(data):
    global is_takeoff
    is_takeoff=0   

my_ref=Twist()
def cb_ref(data):
    global my_ref
    my_ref=data


def F_rep(pos,occ_pos):
    d=0
    d=d+(pos.linear.x-occ_pos.linear.x)**2
    d=d+(pos.linear.y-occ_pos.linear.y)**2
    d=d+((pos.linear.z-occ_pos.linear.z)*2)**2
    d=np.sqrt(d)
    # print(pos,occ_pos)
    R=1.0
    if d>R:
        # print(d)
        return Twist()
    gain=1.0*(1.0/d-1.0/R)/d/d
    ret=Twist()
    ret.linear.x=(pos.linear.x-occ_pos.linear.x)*gain
    ret.linear.y=(pos.linear.y-occ_pos.linear.y)*gain
    ret.linear.z=(pos.linear.z-occ_pos.linear.z)*gain
    return ret

def vec_a2b(a,b):
    ret=Twist()
    ret.linear.x=(b.linear.x-a.linear.x)
    ret.linear.y=(b.linear.y-a.linear.y)
    ret.linear.z=(b.linear.z-a.linear.z)
    return ret

def F_att(pos,t_pos):
    ret=Twist()
    ret.linear.x=(t_pos.linear.x-pos.linear.x)
    ret.linear.y=(t_pos.linear.y-pos.linear.y)
    ret.linear.z=(t_pos.linear.z-pos.linear.z)
    return ret


def dis(pos,occ_pos):
    d=0
    d=d+(pos.linear.x-occ_pos.linear.x)**2
    d=d+(pos.linear.y-occ_pos.linear.y)**2
    d=d+(pos.linear.z-occ_pos.linear.z)**2
    d=np.sqrt(d)
    return d

def inner_prod(pos1,pos2):
    d=0
    d=d+pos1.linear.x*pos2.linear.x
    d=d+pos1.linear.y*pos2.linear.y
    d=d+pos1.linear.z*pos2.linear.z
    return d


isSIM=rospy.get_param('isSIM')

if isSIM==1:
    is_takeoff=1
else:
    is_takeoff=0


class for_occ:
    def __init__(self,i):
        self.sub_now=rospy.Subscriber("/drone"+str(i)+'/from_kf', Twist, self.cb_now)
        self.sub_ref=rospy.Subscriber("/drone"+str(i)+'/ref_aft', Twist, self.cb_ref)
        self.d_now=Twist()
        self.d_ref=Twist()
    def cb_now(self,data):
        self.d_now=data
    def cb_ref(self,data):
        self.d_ref=data




rospy.init_node('local_planner', anonymous=True)
box_sub = rospy.Subscriber('from_kf', Twist, cb_box)

occ_vel_pub = rospy.Publisher('occ_vel', Twist, queue_size=1)
ref_l_pub = rospy.Publisher('ref_l', Twist, queue_size=1)
takeoff_sub = rospy.Subscriber('tello/takeoff', Empty, cb_takeoff)
ref_sub = rospy.Subscriber('ref_aft', Twist, cb_ref)
land_sub = rospy.Subscriber('tello/land', Empty, cb_land)
dis_pub = rospy.Publisher('dis', Twist, queue_size=1)
rate = rospy.Rate(50)


my_namespace=rospy.get_namespace()

print("-------------------",my_namespace)

if my_namespace=="/drone1/":
    occ_list=[1]
elif my_namespace=="/drone2/":
    occ_list=[0]
Tello_list=[1,2]
for_occ_list=[for_occ(i) for i in Tello_list]



while  not rospy.is_shutdown():
    if is_takeoff:

        d_t = 1.0/30
        goalP=F_att(my_data,my_ref)



        occ_f=Twist()
        dd=0
        for i in occ_list:
            # f=F_rep(my_data,for_occ_list[i].d_now)
            # occ_f.linear.x=occ_f.linear.x+f.linear.x
            # occ_f.linear.y=occ_f.linear.y+f.linear.y
            # occ_f.linear.z=occ_f.linear.z+f.linear.z
            dd=dis(my_data,for_occ_list[i].d_now)
            d=Twist()
            d.linear.x=dd
            dd2=dis(my_ref,for_occ_list[i].d_ref)
            d.linear.y=dd2

            inn=0
            UP_B=10
            LOW_B=7
            if dd<10:
                vec_occ=vec_a2b(my_data,for_occ_list[i].d_now)
                inn=inner_prod(goalP,vec_occ)
                if inn<0:
                    inn=0
                if inn>0:
                    inn=inn/(dis(vec_occ,Twist())*dis(vec_occ,Twist()))
                g=(dd-UP_B)/(LOW_B-UP_B)
                occ_f.linear.x=occ_f.linear.x-vec_occ.linear.x*inn*g
                occ_f.linear.y=occ_f.linear.y-vec_occ.linear.y*inn*g
                occ_f.linear.z=occ_f.linear.z-vec_occ.linear.z*inn*g


        dis_pub.publish(d)




        occ_vel_pub.publish(occ_f)
        
        UP_B=3
        LOW_B=0.5

        # if dd<UP_B and dd>LOW_B:
        #     gain=(dd-LOW_B)/(UP_B-LOW_B)
        #     gain=gain**2
        # elif dd>UP_B:
        #     gain=1
        # elif dd<LOW_B:
        #     gain=0
        # print(gain)


        out_msg=Twist()
        # out_msg.linear.x=my_data.linear.x+(goalP.linear.x+occ_f.linear.x)*gain
        # out_msg.linear.y=my_data.linear.y+(goalP.linear.y+occ_f.linear.y)*gain
        # out_msg.linear.z=my_data.linear.z+(goalP.linear.z+occ_f.linear.z)*gain
        out_msg.linear.x=my_data.linear.x+goalP.linear.x+occ_f.linear.x
        out_msg.linear.y=my_data.linear.y+goalP.linear.y+occ_f.linear.y
        out_msg.linear.z=my_data.linear.z+goalP.linear.z+occ_f.linear.z
        out_msg.angular.z=my_ref.angular.z

        ref_l_pub.publish(out_msg)


    rate.sleep()