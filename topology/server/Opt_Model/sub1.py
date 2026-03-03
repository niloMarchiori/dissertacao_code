import numpy as np

def get_TN3(N3,alpha,c,D,kappa):
    T_N3=0
    for ue in N3:
        cd3= (c[ue]*D[ue]).astype(float)**3
        T_N3+=(alpha*cd3)/kappa
    T_N3= T_N3**(1/3)
    return T_N3

def get_TN2(N2,c,D,fmin):
    if not N2:
        return -1
    times=[]
    for ue in N2:
        times.append(c[ue]*D[ue]/fmin[ue])

    T_N2=max(times)
    return T_N2

def solve_SUB1(kappa,N:int,alpha:float,D:int,c:float,fmin:float,fmax=float,**kwargs):

    D=np.array(D)
    c=np.array(c)
    fmin=np.array(fmin)
    fmax=np.array(fmax)

    upper_b_time=c*D/fmin
    ordened_UES=np.argsort(upper_b_time)

    lower_b_time=c*D/fmax
    bottle_neck=np.argsort(lower_b_time)[-1]

    N1=set()
    N2=set()
    N3=set(x for x in range(N))

    T_N1=lower_b_time[bottle_neck]
    T_N2=get_TN2(N2,c,D,fmin)
    T_N3=get_TN3(N3,alpha,c,D,kappa)

    T=max(T_N1, T_N2, T_N3)

    for ue in ordened_UES:
        if not N1 and T_N3>0:
            if T_N1>=T_N3:
                N1.add(bottle_neck)
                N3.remove(bottle_neck)
                T_N3=get_TN3(N3,alpha,c,D,kappa)
        if upper_b_time[ue]<=T:
            N2.add(ue)
            N3.remove(ue)
            T_N3=get_TN3(N3,alpha,c,D,kappa)
            T_N2=get_TN2(N2,c,D,fmin)
            T=max(T_N1, T_N2, T_N3)
    T_N2=get_TN2(N2,c,D,fmin)
    T_cmp=max(T_N3, T_N2, T_N1)
    f=np.zeros(N)
    for ue in N1:
        f[ue]=fmax[ue]/10**9
    for ue in N2:
        f[ue]=fmin[ue]/10**9  
    for ue in N3:
        f[ue]=c[ue]*D[ue]/T_cmp/10**9

    return T_cmp, f