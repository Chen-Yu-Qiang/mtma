#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from control_msgs.msg import PidState
import threading
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
    global box_lock,box_x,box_y,box_z,l_flag,box_ang,my_data
    box_lock.acquire()
    box_x=data.linear.x
    box_y=data.linear.y
    box_z=data.linear.z
    box_ang=data.angular.z
    box_lock.release()
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
    global ref_lock,x_d,y_d,z_d,ang_d,my_ref
    ref_lock.acquire()
    x_d=data.linear.x
    y_d=data.linear.y
    z_d=data.linear.z
    ang_d=data.angular.z
    ref_lock.release()
    my_ref=data


def F_rep(pos,occ_pos):
    d=0
    d=d+(pos.linear.x-occ_pos.linear.x)**2
    d=d+(pos.linear.y-occ_pos.linear.y)**2
    d=d+((pos.linear.z-occ_pos.linear.z))**2
    d=np.sqrt(d)
    # print(pos,occ_pos)
    R=0.8
    if d>R:
        # print(d)
        return Twist()
    gain=0.5*(1.0/d-1.0/R)/d/d
    ret=Twist()
    ret.linear.x=(pos.linear.x-occ_pos.linear.x)*gain
    ret.linear.y=(pos.linear.y-occ_pos.linear.y)*gain
    ret.linear.z=(pos.linear.z-occ_pos.linear.z)*gain
    return ret

def dis(pos,occ_pos):
    d=0
    d=d+(pos.linear.x-occ_pos.linear.x)**2
    d=d+(pos.linear.y-occ_pos.linear.y)**2
    d=d+(pos.linear.z-occ_pos.linear.z)**2
    d=np.sqrt(d)
    return d

isSIM=rospy.get_param('isSIM')

if isSIM==1:
    is_takeoff=1
else:
    is_takeoff=0


class for_occ:
    def __init__(self,i):
        self.sub_now=rospy.Subscriber("/drone"+str(i)+'/from_kf', Twist, self.cb_now)
        self.sub_ref=rospy.Subscriber("/drone"+str(i)+'/ref', Twist, self.cb_ref)
        self.d_now=Twist()
        self.d_ref=Twist()
    def cb_now(self,data):
        self.d_now=data
    def cb_ref(self,data):
        self.d_ref=data




rospy.init_node('control_val_node_kf', anonymous=True)
box_sub = rospy.Subscriber('from_kf', Twist, cb_box)

cmd_val_pub = rospy.Publisher('tello/cmd_vel', Twist, queue_size=1)
occ_vel_pub = rospy.Publisher('occ_vel', Twist, queue_size=1)
v_cmd_pub = rospy.Publisher('v_cmd', Twist, queue_size=1)
v_cmd2_pub = rospy.Publisher('v_cmd2', Twist, queue_size=1)
x_pid_pub = rospy.Publisher('x_pid', PidState, queue_size=1)
y_pid_pub = rospy.Publisher('y_pid', PidState, queue_size=1)
z_pid_pub = rospy.Publisher('z_pid', PidState, queue_size=1)
ang_pid_pub = rospy.Publisher('th_pid', PidState, queue_size=1)
takeoff_sub = rospy.Subscriber('tello/takeoff', Empty, cb_takeoff)
ref_sub = rospy.Subscriber('ref_l', Twist, cb_ref)
land_sub = rospy.Subscriber('tello/land', Empty, cb_land)
rate = rospy.Rate(100)

box_lock=threading.Lock()
ang_lock=threading.Lock()
ref_lock=threading.Lock()

cmd_val_pub_msg=Twist()
x_d = 1
y_d = 0
z_d = 0
ang_d=90
err_x_last=0
err_y_last=0
err_z_last=0
err_ang_last=0
err_x_int=0
err_y_int=0
err_z_int=0
err_ang_int=0


err_x_dif_filter=filter_lib.meanFilter(1)
err_y_dif_filter=filter_lib.meanFilter(1)
err_z_dif_filter=filter_lib.meanFilter(1)
err_ang_dif_filter=filter_lib.meanFilter(1)


my_namespace=rospy.get_namespace()

print("-------------------",my_namespace)

if my_namespace=="/drone1/":
    occ_list=[1]
elif my_namespace=="/drone2/":
    occ_list=[0]
Tello_list=[1,2]
# for_occ_list=[for_occ(i) for i in Tello_list]

while  not rospy.is_shutdown():
    if is_takeoff:

        d_t = 1.0/100.0

        box_lock.acquire()
        x_now = box_x
        y_now = box_y
        z_now = box_z
        ang_now = box_ang
        box_lock.release()


        x_pid=PidState()
        y_pid=PidState()
        z_pid=PidState()
        ang_pid=PidState()

        ref_lock.acquire()
        err_x = x_d - x_now
        err_y = y_d - y_now
        err_z = z_d - z_now
        # if abs(ang_d - ang_now)>abs(ang_d - ang_now+np.pi*2):
        #     err_ang = ang_d - ang_now + np.pi*2
        # elif abs(ang_d - ang_now)>abs(ang_d - ang_now-np.pi*2):
        #     err_ang = ang_d - ang_now - np.pi*2
        # else:
        #     err_ang = ang_d - ang_now
        err_ang = ang_d - ang_now
        ref_lock.release()        





        err_x_dif_o = (err_x - err_x_last) / d_t
        err_x_dif=err_x_dif_filter.update(err_x_dif_o)
        err_x_int = err_x_int + err_x * d_t
        err_x_last = err_x

        
        err_y_dif_o = (err_y - err_y_last) / d_t
        err_y_dif=err_y_dif_filter.update(err_y_dif_o)
        err_y_int = err_y_int + err_y * d_t
        err_y_last = err_y

        
        err_z_dif_o = (err_z - err_z_last) / d_t
        err_z_dif=err_z_dif_filter.update(err_z_dif_o)
        err_z_int = err_z_int + err_z * d_t
        err_z_last = err_z


        err_ang_dif_o = (err_ang - err_ang_last) / d_t
        err_ang_dif=err_ang_dif_filter.update(err_ang_dif_o)
        err_ang_int = err_ang_int + err_ang * d_t
        err_ang_last = err_ang
        
        kp = 1.5
        ki = 0.3
        kd = 1.8

        #if abs(err_x)>0.7:
        #    kp = 10000
        #elif abs(err_x)>0.55:
        #    kp = -10000
        #else:
        #    kp = 1
        #    ki = 0.1
        #    kd = 0.5
        cmd_x=kp*err_x+ki*err_x_int+kd*err_x_dif
        x_pid.error=err_x
        x_pid.p_error=err_x
        x_pid.i_error=err_x_int
        x_pid.error_dot=err_x_dif_o
        x_pid.d_error=err_x_dif
        x_pid.p_term=kp
        x_pid.i_term=ki
        x_pid.d_term=kd
        x_pid.output=cmd_x


        cmd_y=kp*err_y+ki*err_y_int+kd*err_y_dif
        y_pid.error=err_y
        y_pid.p_error=err_y
        y_pid.i_error=err_y_int
        y_pid.error_dot=err_y_dif_o
        y_pid.d_error=err_y_dif
        y_pid.p_term=kp
        y_pid.i_term=ki
        y_pid.d_term=kd
        y_pid.output=cmd_y


        kp = 2
        ki = 0
        kd = 0
        cmd_z=kp*err_z+ki*err_z_int+kd*err_z_dif
        z_pid.error=err_z
        z_pid.p_error=err_z
        z_pid.i_error=err_z_int
        z_pid.error_dot=err_z_dif_o
        z_pid.d_error=err_z_dif
        z_pid.p_term=kp
        z_pid.i_term=ki
        z_pid.d_term=kd
        z_pid.output=cmd_z



        kp = 1
        ki = 0
        kd = 0
        cmd_ang=kp*err_ang+ki*err_ang_int+kd*err_ang_dif
        # cmd_ang=cmd_ang
        ang_pid.error=err_ang
        ang_pid.p_error=err_ang
        ang_pid.i_error=err_ang_int
        ang_pid.error_dot=err_ang_dif_o
        ang_pid.d_error=err_ang_dif
        ang_pid.p_term=kp
        ang_pid.i_term=ki
        ang_pid.d_term=kd
        ang_pid.output=cmd_ang



        LIM=1
        # ==========world frame===============
        v_cmd_msg=Twist()

        v_cmd_msg.linear.x = cmd_x
        v_cmd_msg.linear.y = cmd_y
        v_cmd_msg.linear.z = cmd_z
        v_cmd_msg.angular.z = -cmd_ang
        if abs(v_cmd_msg.linear.x)>LIM:
            v_cmd_msg.linear.x=v_cmd_msg.linear.x/abs(v_cmd_msg.linear.x)*LIM
        if abs(v_cmd_msg.linear.y)>LIM:
            v_cmd_msg.linear.y=v_cmd_msg.linear.y/abs(v_cmd_msg.linear.y)*LIM
        if abs(v_cmd_msg.linear.z)>LIM:
            v_cmd_msg.linear.z=v_cmd_msg.linear.z/abs(v_cmd_msg.linear.z)*LIM
        if abs(v_cmd_msg.angular.z)>LIM:
            v_cmd_msg.angular.z=v_cmd_msg.angular.z/abs(v_cmd_msg.angular.z)*LIM
        v_cmd_pub.publish(v_cmd_msg)

        # ==========world frame===============

        # occ_f=Twist()
        # dd=0
        # for i in occ_list:
        #     f=F_rep(my_data,for_occ_list[i].d_now)
        #     occ_f.linear.x=occ_f.linear.x+f.linear.x
        #     occ_f.linear.y=occ_f.linear.y+f.linear.y
        #     occ_f.linear.z=occ_f.linear.z+f.linear.z
        #     dd=dis(my_data,for_occ_list[i].d_now)
        #     d=Twist()
        #     d.linear.x=dd




        # occ_vel_pub.publish(occ_f)
        # cmd_x=cmd_x+occ_f.linear.x
        # cmd_y=cmd_y+occ_f.linear.y
        # cmd_z=cmd_z+occ_f.linear.z


        # for i in occ_list:
        #     dd=dis(my_ref,for_occ_list[i].d_ref)
        # gain=1
        # d0=0.75
        # d1=1
        # if dd<d0:
        #     gain=0
        # elif dd>d1:
        #     gain=1
        # elif dd<d1:
        #     gain=((dd-d0)/(d1-d0))**3


        # cmd_x=cmd_x*gain
        # cmd_y=cmd_y*gain
        # cmd_z=cmd_z*gain

        v_cmd2_msg=Twist()
        v_cmd2_msg.linear.x = cmd_x
        v_cmd2_msg.linear.y = cmd_y
        v_cmd2_msg.linear.z = cmd_z
        v_cmd2_msg.angular.z = -cmd_ang
        v_cmd2_pub.publish(v_cmd2_msg)


        # =======to drone frame===============
        if l_flag==0:
            # cmd_val_pub_msg.linear.x = cmd_y
            # cmd_val_pub_msg.linear.y = -cmd_x
            cmd_val_pub_msg.linear.x = np.cos(ang_now)*cmd_x+np.sin(ang_now)*cmd_y
            cmd_val_pub_msg.linear.y = -np.sin(ang_now)*cmd_x+np.cos(ang_now)*cmd_y
            cmd_val_pub_msg.linear.z = cmd_z
            cmd_val_pub_msg.angular.z = -cmd_ang
        else:
            cmd_val_pub_msg.linear.x = 0
            cmd_val_pub_msg.linear.y = 0
            cmd_val_pub_msg.angular.z = 0
            cmd_val_pub_msg.angular.z = 0


        if abs(cmd_val_pub_msg.linear.x)>LIM:
            cmd_val_pub_msg.linear.x=cmd_val_pub_msg.linear.x/abs(cmd_val_pub_msg.linear.x)*LIM
        if abs(cmd_val_pub_msg.linear.y)>LIM:
            cmd_val_pub_msg.linear.y=cmd_val_pub_msg.linear.y/abs(cmd_val_pub_msg.linear.y)*LIM
        if abs(cmd_val_pub_msg.linear.z)>LIM:
            cmd_val_pub_msg.linear.z=cmd_val_pub_msg.linear.z/abs(cmd_val_pub_msg.linear.z)*LIM
        if abs(cmd_val_pub_msg.angular.z)>LIM:
            cmd_val_pub_msg.angular.z=cmd_val_pub_msg.angular.z/abs(cmd_val_pub_msg.angular.z)*LIM
        
        #print(cmd_val_pub_msg.linear)

        if isSIM==0:
            cmd_val_pub.publish(cmd_val_pub_msg)

        # =======to drone frame===============

        x_pid_pub.publish(x_pid)
        y_pid_pub.publish(y_pid)
        z_pid_pub.publish(z_pid)
        ang_pid_pub.publish(ang_pid)

    rate.sleep()