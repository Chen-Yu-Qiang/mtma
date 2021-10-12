#!/usr/bin/env python
#%%
from viewPanning import *

import matplotlib.pyplot as plt
aa_ci=[0.0, -2.938368100710985, 0.9, 0.1327]



def f(x,y):
    C_s_sum=0
    _ci=[x,y,aa_ci[2],aa_ci[3]]
    for i in range(len(taskPoint)):
        C_s_sum=C_s_sum+C_s(taskPoint[i],_ci)
        # if C_s(taskPoint[i],_ci)==0:
        #     return 0
    return C_s_sum
def C_s_all(ci,taskPoint):
    C_s_sum=0
    _ci=[ci[0],ci[1],ci[2],ci[3]]
    for i in range(len(taskPoint)):
        C_s_sum=C_s_sum+C_s(taskPoint[i],_ci)
        # if C_s(taskPoint[i],_ci)==0:
        #     return 0
    return C_s_sum

board_color=["tab:orange","tab:green"]
# taskPoint=[[-1.1,1.0,0.9,-0.1],[1.1,1.0,0.9,0.1],[0.1,1.0,0.9,0.1],[1.1,0.5,0.9,0.05],[1,1.0,0.9,0.0]]
taskPoint=[[1.1,0.5,0.9,0.05]]


# for contourf=======================================================
x_list=np.linspace(-5,5,41)
y_list=np.linspace(-5,5,41)
it_num=100
ci_list=[[0,0,0,0] for i in range(it_num)]
Cs_list=[0 for i in range(it_num)]

#%%

Z=[[0 for i in range(len(x_list))]for j in range(len(y_list))]
for i in range(len(x_list)):
        for j in range(len(y_list)):
            Z[j][i]=f(x_list[i],y_list[j])
            # print(x_list[i],y_list[j],Z[j][i])
max_Z=-2
for i in range(len(x_list)):
        for j in range(len(y_list)):
            if Z[j][i]>max_Z:
                max_Z=Z[j][i]
                print(x_list[i],y_list[j],Z[j][i])

plt.contourf(x_list, y_list, Z,100,cmap='jet')
plt.colorbar()    
# plt.axis([-5,5,-5,5])
# plt.scatter(res.linear.x,res.linear.y)
# [x,xx],[y,yy]=v_y(res.linear.x,res.linear.y,res.angular.z,0.3)
# plt.plot([x,xx],[y,yy])    

for i in range(len(taskPoint)):
    plt.scatter(taskPoint[i][0],taskPoint[i][1],color=board_color[0])
    [x,xx],[y,yy]=v_y(taskPoint[i][0],taskPoint[i][1],taskPoint[i][3])
    plt.plot([x,xx],[y,yy],color=board_color[0])

plt.scatter(aa_ci[0],aa_ci[1],color=board_color[1])
[x,xx],[y,yy]=v_y(aa_ci[0],aa_ci[1],aa_ci[3],0.5)
plt.plot([x,xx],[y,yy],color=board_color[1])

vp=viewPanner()
vp.set_taskPoint(taskPoint)
vp.ci=[3, -1, 0.9, 0.5]
vp.bata=0
tck1_1=[0 for i in range(it_num)]
tck1_2=[0 for i in range(it_num)]
tck1_3=[0 for i in range(it_num)]
tck1_4=[0 for i in range(it_num)]
tck2_1=[0 for i in range(it_num)]
tck2_2=[0 for i in range(it_num)]
tck2_3=[0 for i in range(it_num)]
tck2_4=[0 for i in range(it_num)]
vp.it_length=20
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
t=time.time()
aa=1
for i in range(it_num):
    aa=aa*0.9
    vp.one_it_steepest(aa)
    vp.it_length=vp.it_length
    ci_list[i]=vp.ci[:]
    Cs_list[i]=C_s_all(vp.ci,taskPoint)
    cpk=worldFrame2CameraFrame(taskPoint[0],vp.ci)
    tpk=ciSpace2tiSpace(cpk)

    tck1_1[i]=abs(tpk[0])
    tck1_2[i]=abs(tpk[1])
    tck1_3[i]=abs(tpk[2])
    tck1_4[i]=abs(tpk[3])

    cpk=worldFrame2CameraFrame(taskPoint[0],vp.ci)
    tpk=ciSpace2tiSpace(cpk)

    tck2_1[i]=abs(tpk[0])
    tck2_2[i]=abs(tpk[1])
    tck2_3[i]=abs(tpk[2])
    tck2_4[i]=abs(tpk[3])
    if i>=0:
        plt.scatter(vp.ci[0],vp.ci[1],color=board_color[1])
        [x,xx],[y,yy]=v_y(vp.ci[0],vp.ci[1],vp.ci[3],0.5)
        plt.plot([x,xx],[y,yy],color=board_color[1])



        plt.draw()
        plt.pause(0.01)
        # plt.clf()
        print(vp.ci,C_s_all(vp.ci,taskPoint))
print("total time: ",time.time()-t)
plt.show()
plt.subplot(4,1,1)
plt.plot([ci_list[i][0] for i in range(it_num)])
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel("X (m)")

plt.subplot(4,1,2)
plt.plot([ci_list[i][1] for i in range(it_num)])
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel("Y (m)")

plt.subplot(4,1,3)
plt.plot([ci_list[i][2] for i in range(it_num)])
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel("Z (m)")

plt.subplot(4,1,4)
plt.plot([ci_list[i][3] for i in range(it_num)])
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel("Theta (rad)")

plt.show()

plt.plot(Cs_list)
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel("C_s")

plt.show()

plt.plot(tck1_1)
plt.plot(tck1_2)
plt.plot(tck1_3)
plt.plot(tck1_4)
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel(" (m)")
# plt.axis([0,200,-1.5,1.5])
plt.legend(["tp_xk","tp_yk","tp_zk","tp_thk"])
plt.show()


plt.plot(tck2_1)
plt.plot(tck2_2)
plt.plot(tck2_3)
plt.plot(tck2_4)
plt.grid(True)
plt.xlabel("Number of iterations")
plt.ylabel(" (m)")
# plt.axis([0,200,-1.5,1.5])
plt.legend(["tp_xk","tp_yk","tp_zk","tp_thk"])
plt.show()

#%%
ff1=plt.figure()
f1=ff1.add_subplot(1,1,1)
f2=plt.figure(2)
sf1=f2.add_subplot(4,1,1)
sf2=f2.add_subplot(4,1,2)
sf3=f2.add_subplot(4,1,3)
sf4=f2.add_subplot(4,1,4)
for it_rate in [1,0.99,0.95,0.9,0.8]:
    t=time.time()
    vp=viewPanner()
    vp.set_taskPoint(taskPoint)
    vp.ci=[0,-1,0,0]

    vp.it_length=1
    for i in range(it_num):
        vp.one_it()
        vp.it_length=vp.it_length*it_rate
        ci_list[i]=vp.ci[:]
        Cs_list[i]=C_s_all(vp.ci,taskPoint)
        if i>100:
            f1.scatter(vp.ci[0],vp.ci[1],color=board_color[1])
            [x,xx],[y,yy]=v_y(vp.ci[0],vp.ci[1],vp.ci[3],0.5)
            f1.plot([x,xx],[y,yy],color=board_color[1])
            ff1.canvas.draw_idle() 
            plt.pause(0.01)
            # plt.clf()
        if i==198:
            print(it_rate,vp.ci,C_s_all(vp.ci,taskPoint))
    print(time.time()-t)
    f1.plot(Cs_list)
    sf1.plot([ci_list[i][0] for i in range(it_num)])
    sf2.plot([ci_list[i][1] for i in range(it_num)])
    sf3.plot([ci_list[i][2] for i in range(it_num)])
    sf4.plot([ci_list[i][3] for i in range(it_num)])

f1.grid(True)
f1.set_xlabel("Number of iterations")
f1.set_ylabel("C_s")
f1.legend(["1","0.99","0.95","0.9","0.8"])
ff1.show()



sf1.grid(True)
sf1.set_xlabel("Number of iterations")
sf1.set_ylabel("X (m)")
sf2.grid(True)
sf2.set_xlabel("Number of iterations")
sf2.set_ylabel("Y (m)")
sf3.grid(True)
sf3.set_xlabel("Number of iterations")
sf3.set_ylabel("Z (m)")
sf4.grid(True)
sf4.set_xlabel("Number of iterations")
sf4.set_ylabel("Theta (rad)")
sf1.legend(["1","0.99","0.95","0.9","0.8"])
f2.show()
plt.show()
# %%
def C_s_all(ci,taskPoint):
    C_s_sum=0
    _ci=[ci[0],ci[1],ci[2],ci[3]]
    for i in range(len(taskPoint)):
        C_s_sum=C_s_sum+C_s(taskPoint[i],_ci)
        # if C_s(taskPoint[i],_ci)==0:
        #     return 0
    return C_s_sum
t=time.time()

max_ci=[0,0,0,0]
max_cs=0
ci_lim1=[-5,-5,0,-0.1]
ci_lim2=[5,5,5,0.1]
N_equ_part=20
for m in range(5):
    for i in np.linspace(ci_lim1[0],ci_lim2[0],N_equ_part+1):
        for j in np.linspace(ci_lim1[1],ci_lim2[1],N_equ_part+1):
            for k in np.linspace(ci_lim1[2],ci_lim2[2],N_equ_part+1):
                for l in np.linspace(ci_lim1[3],ci_lim2[3],N_equ_part+1):
                    ci=[i,j,k,l]
                    a=C_s_all(ci,taskPoint)
                    if a>max_cs:
                        max_cs=a
                        max_ci=ci
    print(max_ci,max_cs)
    for i in range(4):
        ci_lim1[i]=max_ci[i]-((ci_lim2[i]-ci_lim1[i])/N_equ_part)
        ci_lim2[i]=max_ci[i]+((ci_lim2[i]-ci_lim1[i])/N_equ_part)

print(time.time()-t)
# # %%
# ci_lim1=[-5,-5,0,-np.pi]
# ci_lim2=[5,0,5,np.pi]
# N_equ_part=40
# it_num=200

# for i in [-1] :
#     for j in [1]:
#         for k in [0.9]:
#             for l in np.linspace(ci_lim1[3],ci_lim2[3],N_equ_part+1):
#                 t=time.time()
#                 vp=viewPanner()
#                 vp.set_taskPoint(taskPoint)
#                 vp.ci=[i,j,k,l]

#                 vp.it_length=1
#                 for m in range(it_num):
#                         vp.one_it()
#                         vp.it_length=vp.it_length
#                 if C_s_all(vp.ci,taskPoint)<0.8:
#                     print([i,j,k,l],C_s_all(vp.ci,taskPoint))


# %%
