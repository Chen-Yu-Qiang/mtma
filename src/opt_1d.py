#!/usr/bin/env python


rou=0.381966

def gold_div_search(a,b,fun,esp=0.001):
    data=list()
    x1=a+rou*(b-a)
    x2=b-rou*(b-a)
    data.append([a,x1,x2,b])
    while((b-a)>esp):
        f1=fun(x1)
        f2=fun(x2)
        if f1>f2:
            a=x1
            x1=x2
            x2=b-rou*(b-a)
        elif f1<f2:
            b=x2
            x2=x1
            x1=a+rou*(b-a)
        else:
            a=x1
            b=x2
            x2=b-rou*(b-a)
            x1=a+rou*(b-a)
        
        data.append([a,x1,x2,b])
    
    return (a+b)/2

def gold_div_search_vet(a,b,fun,esp=0.001):
    data=list()

    def a_add_b(a,b):
        c=[0 for i in range(len(a))]
        for i in range(len(a)):
            c[i]=a[i]+b[i]
        return c

    def a_sub_b(a,b):
        c=[0 for i in range(len(a))]
        for i in range(len(a)):
            c[i]=a[i]-b[i]
        return c

    def a_mul_b(a,b):
        c=[0 for i in range(len(b))]
        for i in range(len(b)):
            c[i]=a*b[i]
        return c        

    def dis(a):
        c=0
        for i in range(len(a)):
            c=c+a[i]*a[i]
        return c        


    x1=a_add_b(a,a_mul_b(rou,a_sub_b(b,a)))
    x2=a_sub_b(b,a_mul_b(rou,a_sub_b(b,a)))
    # data.append([a,x1,x2,b])
    while(dis(a_sub_b(b,a))>esp):
        f1=fun(x1)
        f2=fun(x2)
        if f1>f2:
            a=x1
            x1=x2
            x2=a_sub_b(b,a_mul_b(rou,a_sub_b(b,a)))
        elif f1<f2:
            b=x2
            x2=x1
            x1=a_add_b(a,a_mul_b(rou,a_sub_b(b,a)))
        else:
            a=x1
            b=x2
            x2=a_sub_b(b,a_mul_b(rou,a_sub_b(b,a)))
            x1=a_add_b(a,a_mul_b(rou,a_sub_b(b,a)))
        # data.append([a,x1,x2,b])
        # print(a,b,f1,f2)
    
    return a_mul_b(0.5,a_add_b(a,b))

if __name__=="__main__":
    def foo(x):
        return (2.71828)**(-x)+x**2
    
    print(gold_div_search(0,1,foo))