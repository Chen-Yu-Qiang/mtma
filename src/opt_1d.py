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

if __name__=="__main__":
    def foo(x):
        return (2.71828)**(-x)+x**2
    
    print(gold_div_search(0,1,foo))