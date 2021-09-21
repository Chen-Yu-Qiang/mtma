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
import positioning_board

dt=1.0/30.0

class ros_viewPlanner:
    def __init__(self,myname):
        self.str_name=myname
        self.vper=viewPanning.viewPanner()
        self.vper.myName=myname
        self.ci_pub=rospy.Publisher('plan_wp_'+self.str_name, Twist, queue_size=1)
        self.tpk_pub=rospy.Publisher('plan_tpk_'+self.str_name, Float32MultiArray, queue_size=1)
        self.t=None
        # self.vper.set_occ([[3.3,1,1.2,0]])
        self.ci=Twist()
        self.is_Covered=1
    def set_taskPoint(self,t):
        self.vper.set_taskPoint(t)

    def set_ci(self,_ci):
        self.ci=_ci
        self.vper.ci=_ci

    def pub_ci(self,time=100):
        res=viewPanning.ci2twist(self.vper.gant(times=time))
        # print(self.res)
        self.ci_pub.publish(res)
        self.ci=res
    
    def pub_ci_start(self,times=100):
        self.t=threading.Thread(target=self.pub_ci,args=(times,))
        self.t.start()

    def pub_ci_end(self):
        self.t.join()
    
    def pub_tpk(self):
        d=self.vper.get_tpk()
        dd=Float32MultiArray(data=d)
        self.tpk_pub.publish(dd)


class target:
    def __init__(self,_i):
        self.sub = rospy.Subscriber('target'+str(_i)+"_f", Twist, self.cb_fun)
        self.sub2 = rospy.Subscriber('target'+str(_i)+"_f_future", Twist, self.cb_fun2)
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

class uav:
    def __init__(self,i):
        self.sub=rospy.Subscriber("/drone"+str(i)+'/from_kf', Twist, self.cb)
        self.d=None
        self.data=Twist()
        self.i=i
    def cb(self,data):
        self.d=viewPanning.twist2ci(data)
        self.data=data
        # print(self.i,self.d)

rospy.init_node('plan_node', anonymous=True)


Tello_list=[1,2]
target_set=[target(i) for i in range(51,60)]
uav_set=[uav(i) for i in Tello_list]
ref_raw_pub_list = [rospy.Publisher("drone"+str(i)+'/ref_bef_pre', Twist, queue_size=1) for i in Tello_list]
plan_res_pub=rospy.Publisher('/plan_res', Float32MultiArray, queue_size=1)
rate = rospy.Rate(30)

rvp_52=ros_viewPlanner("52")


rvp_51_future=ros_viewPlanner("51_future")
rvp_52_future=ros_viewPlanner("52_future")
rvp_51_f_p=ros_viewPlanner("51_future_pos")
rvp_52_f_p=ros_viewPlanner("52_future_pos")



def dis(uav,plan_res):
    return np.sqrt((uav.linear.x-plan_res.linear.x)**2+(uav.linear.y-plan_res.linear.y)**2+(uav.linear.z-plan_res.linear.z)**2)



ref_board=Twist()
ref_board.linear.x=0
ref_board.linear.y=0
ref_board.linear.z=0.9
ref_board.angular.z=np.pi*0.5
MODE=2
while not rospy.is_shutdown():

    if (not target_set[0].isTimeout()) and (not target_set[1].isTimeout()):
        t=time.time()


        taskPoint=viewPanning.twist2taskpoint([target_set[0].data,target_set[0].future])
        taskPoint=viewPanning.board_Expand(taskPoint)
        # rvp_51_future.vper.set_occ([uav_set[0].d])
        rvp_51_future.set_taskPoint(taskPoint)


        taskPoint=viewPanning.twist2taskpoint([target_set[1].data,target_set[1].future])
        taskPoint=viewPanning.board_Expand(taskPoint)
        # rvp_52_future.vper.set_occ([uav_set[1].d])
        rvp_52_future.set_taskPoint(taskPoint)


        _,_,pos=positioning_board.what_nearEst(target_set[0].data)
        taskPoint=viewPanning.twist2taskpoint([pos,target_set[0].data,target_set[0].future])
        taskPoint=viewPanning.board_Expand(taskPoint)
        rvp_51_f_p.set_taskPoint(taskPoint)

        _,_,pos=positioning_board.what_nearEst(target_set[1].data)
        taskPoint=viewPanning.twist2taskpoint([pos,target_set[1].data,target_set[1].future])
        taskPoint=viewPanning.board_Expand(taskPoint)
        rvp_52_f_p.set_taskPoint(taskPoint)

        # rvp_51_future.pub_ci_start(20)
        # rvp_51_future.pub_ci_end()
        # rvp_52_future.pub_ci_start(20)
        # rvp_52_future.pub_ci_end()
        # rvp_51_f_p.pub_ci_start(20)
        # rvp_51_f_p.pub_ci_end()
        # rvp_52_f_p.pub_ci_start(20)
        # rvp_52_f_p.pub_ci_end()

        rvp_51_future.pub_ci(20)
        rvp_51_future.pub_tpk()


        rvp_52_future.pub_ci(20)
        rvp_52_future.pub_tpk()

        rvp_51_f_p.pub_ci(20)
        rvp_51_f_p.pub_tpk()



        rvp_52_f_p.pub_ci(20)
        rvp_52_f_p.pub_tpk()


        rvp_51_f_p.is_Covered=viewPanning.isCovered(viewPanning.twist2ci(rvp_51_f_p.ci),rvp_51_f_p.vper.taskPoint)
        rvp_52_f_p.is_Covered=viewPanning.isCovered(viewPanning.twist2ci(rvp_52_f_p.ci),rvp_52_f_p.vper.taskPoint)



        # print(time.time()-t)

        if rvp_51_f_p.is_Covered==1:
            t51=rvp_51_f_p.ci
        else:
            t51=rvp_51_future.ci

        if rvp_52_f_p.is_Covered==1:
            t52=rvp_52_f_p.ci
        else:
            t52=rvp_52_future.ci

        d51_u1=dis(uav_set[0].data,t51)
        d52_u1=dis(uav_set[0].data,t52)
        d51_u2=dis(uav_set[1].data,t51)
        d52_u2=dis(uav_set[1].data,t52)


        if (d51_u1+d52_u2)<(d51_u2+d52_u1):
            rvp_51_future.vper.set_occ([uav_set[1].d])
            rvp_52_future.vper.set_occ([uav_set[0].d])
            ref_raw_pub_list[0].publish(t51)
            ref_raw_pub_list[1].publish(t52)
            # print((d51_u1+d52_u2),(d51_u2+d52_u1),"mode 1")
            MODE=1

        else:
            rvp_51_future.vper.set_occ([uav_set[0].d])
            rvp_52_future.vper.set_occ([uav_set[1].d])
            ref_raw_pub_list[0].publish(t52)
            ref_raw_pub_list[1].publish(t51)
            # print((d51_u1+d52_u2),(d51_u2+d52_u1),"mode 2")
            MODE=2

        plan_res_msg=[MODE,d51_u1+d52_u2,d51_u2+d52_u1,rvp_51_f_p.is_Covered,rvp_52_f_p.is_Covered]
        plan_res_msg=Float32MultiArray(data=plan_res_msg)
        plan_res_pub.publish(plan_res_msg)

    rate.sleep()