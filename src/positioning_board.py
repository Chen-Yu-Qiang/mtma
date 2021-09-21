#!/usr/bin/env python

from geometry_msgs.msg import Twist
import viewPanning
import numpy as np

N=1
data=[Twist() for i in range(N)]

data[0]=Twist()
data[0].linear.x=0
data[0].linear.y=0
data[0].linear.z=0.9
data[0].angular.z=np.pi*0.5



def dis(uav,plan_res):
    return np.sqrt((uav.linear.x-plan_res.linear.x)**2+(uav.linear.y-plan_res.linear.y)**2+(uav.linear.z-plan_res.linear.z)**2)


def what_nearEst(pos):
    d_near=dis(pos,data[0])
    i_near=0

    for i in range(1,len(data)):
        d=dis(pos,data[i])
        if d<d_near:
            d_near=d
            i_near=i
    return i_near,d_near,data[i_near]

