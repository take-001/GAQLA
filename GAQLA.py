import random
import math
import time
from itertools import chain
import numpy as np
from pyomo.opt import TerminationCondition


class GAQLA:
    def __init__(self,seed,K=3,C=2,Q=5,q_label=30,N_pool=80,mu=0.5,l=0.1): # seed/OD/Customer/capa/q/N_pool/l-tournament
        random.seed(seed)
        self.M=10000
        self.q_label=q_label
        self.K=K
        self.C=C
        self.N_pool=N_pool
        self.Q=Q
        self.l=l
        self.mu=mu
        k,c=self.K,self.C


        self.node=[[random.random(),random.random()] for i in range(k+c+1)]
        #distance matrix(time, minutes)-depot,destinations,customer
        self.T=[[math.sqrt((self.node[i][0]-self.node[j][0])**2+(self.node[i][1]-self.node[j][1])**2)*30 for i in range(k+c+1)] for j in range(k+c+1)]
        for i in range(k+c+1):
            for j in range(i+1,k+c+1):
                self.T[i][j]=self.T[j][i] 
        for i in range(k+c+1): self.T[i][i]=1000000

        #preference matrix
        self.P=[random.random() for i in range(k)]
        #deadline for OC
        self.D_k=[self.T[0][1+c+i]+random.random()*30 for i in range(k)]
        #deadline for C
        self.D_c=[random.random()*60 for i in range(c)]
        self.R_c=[random.random()*10 for i in range(c)]
        self.Deadline=[10000000000]+self.D_c+self.D_k

    def q_labelling(self):
        k, c, load = self.K, self.C, self.Q
        possibles=[]
    
        for idx in range(k):
            end_cond=False
            dead=[0]+self.D_c+self.D_k
            P=[]
            cst={cs for cs in range(1,c+1) if (pp:=self.R_c[cs-1]+self.T[0][cs])<=self.D_c[cs-1] and pp+self.T[cs][1+c+idx]<=self.D_k[idx]}
            if cst:
                cst.add(1+c+idx)
        
                
                l_0=(0,0,0,100000,0,0,0) #(arrival time | -1* #of customer visit |  max rt |  min slack | latter | cur | label id)
                
                nodes_bucket={i:[] for i in cst}
                nodes_bucket[0] = [l_0]
                U=[l_0[5:7]]
                

                while U:
                    Q = U.pop()
                    for i in nodes_bucket[Q[0]]:
                        if i[-1] == Q[-1] and -i[1] < load and i[5] != 1+c+idx:
                            for k in reversed(list(cst - {i[4],i[5]})) : 

                                R_c= (i[2] if k == 1 + c + idx else max(self.R_c[k - 1],i[2])) #max rt
                                dur = i[0] + R_c - i[2] + self.T[i[5]][k]
                                ms = min(i[3], dead[k]-dur)
                                
                        
                                if dur <=dead[k] and ms >= R_c - i[2]:
                                    n_l = (dur, i[1] - 1, R_c, ms, i[5], k, i[-1] + random.random())
                                    
                                    
                                    if nodes_bucket[k]:
                                        app= False
                                        for j in nodes_bucket[k]:
                                            if any(x > y  for x, y in zip(j[:2], n_l[:2])) or any(x < y  for x, y in zip(j[2:4], n_l[2:4])) :
                                                app=True
                                                if all(x > y for x, y in zip(j[:2],n_l[:2])) and all(x < y  for x, y in zip(j[2:4], n_l[2:4])):
                                                    nodes_bucket[k].remove(j)
                                                
                                        if app :
                                            nodes_bucket[k].append(n_l)
                                            U.append(n_l[5:7])                                                
                                                         
                                                
                                    else:
                                           

                                        nodes_bucket[k].append(n_l)
                                        U.append(n_l[5:7])
                                if  k ==1+idx+c and nodes_bucket[1+idx+c]:
                                       
                                    path = self.backtr(nodes_bucket[1+idx+c].pop(),nodes_bucket,idx)
                                    if path : P.append(path)
                                    if len(P)== self.q_label : 
                                        end_cond= True
                                        break

                            break
                    if end_cond : U=False
            possibles.append(P)

        return possibles

    def backtr(self, label, bucket, idx):
        
        c = self.C
        pp = []

        # Find the first matching element in bucket[label[3]]
        l = next((x for x in bucket[label[4]] if np.isclose(x[0], label[0] - self.T[label[4]][1 + c + idx], atol=0.0001)), label)
       
        if l[5]!=0 and l[5]!=1+c+idx:
            pp.insert(0,l[5])
            while  l[4] != 0:
            
                code = (l[0] - self.T[l[4]][l[5]] - l[2] + self.R_c[l[4]-1] if l[2] == self.R_c[l[5] - 1] else l[0] - self.T[l[4]][l[5]])

                # Find the first element that satisfies the condition in the bucket
                
                x = next((x for x in bucket[l[4]] if np.isclose(x[0], code, atol=0.0001)), None)

                if x is not None:
                    pp.insert(0,l[4])
                    l = x
                else:
                    pp=[]
                    break
                
        return pp

    def fitness(self, route):
        fitness=0
        cus={i+1:[] for i in range(self.C)}
        for i in range(len(route)):
            for j in route[i]:
                cus[j].append(i)   
        for i in range(self.C):
            pt_ft=0
            if cus[i+1]:
                pt_ft=1
                for j in cus[i+1]:
            
                    pt_ft=pt_ft*(1-self.P[j])
                pt_ft=1-pt_ft
            fitness+=pt_ft

        return fitness

    def print_sol(self, objective, sol,time):
        k=0
        print("***solution pannel***")
        print("running time: "+f"{time}")
        print("objective: "+f'{objective}')
        print("solution:")
        for i in sol:
            if not i:
                print(f"K{k}: depot -> Destination ({self.T[0][1+self.C+k]},{self.Deadline[1+self.C+k]})")
            else:
                rt_set=[self.R_c[j-1] for j in i]
                temp=0
                duration=max(rt_set)
                line=f"K{k}: depot ->"
                for j in i:
                    duration+=self.T[temp][j]
                    line+=f" C{j} ({duration},{self.Deadline[j]}) ->"
                    temp=j
                line+=f" Destination ({duration+self.T[j][1+self.C+k]},{self.Deadline[1+self.C+k]})"
                print(line)
            k=k+1

    def GAQLA(self):
        st=time.time()
        t=0
        N_pool=self.N_pool
        l=int(self.l*N_pool)
        mu=int(self.mu*N_pool)
       
        
        #finding possible routes
        possible_routes=self.q_labelling()
        
        #make chromsome
        condition=True
        chrsms=[]
        for i in range(N_pool):
            chrm=[]
            for j in possible_routes:
                if j:
                    gene=random.sample(j,1)
                    chrm.append(gene[0])
                else: chrm.append([])
            chrsms.append(chrm)
        #start
        pre_scores={self.fitness(i):i for i in chrsms}
        pre_opt=max(pre_scores)
        pre_sol=pre_scores[pre_opt]
        while condition:
            
            n_chrsms=[]


            #crossover(40)
            for i in range(int((N_pool-mu)/2)):
                ca1={a:self.fitness(chrsms[a]) for a in random.sample(range(N_pool),l)}
                pf1=chrsms[max(ca1, key=ca1.get)]
                ca2={a:self.fitness(chrsms[a]) for a in random.sample(range(N_pool),l)}
                pf2=chrsms[max(ca2, key=ca2.get)]
                p1=random.randrange(1,len(pf1)-1)
                ch1=pf1[:p1]+pf2[p1:]
                ch2=pf2[:p1]+pf1[p1:]
                n_chrsms.append(ch1)
                n_chrsms.append(ch2)
            #mutation(10)
            for i in range(mu):
                chrm=[]
                for j in possible_routes:
                    if j:
                        gene=random.sample(j,1)
                        chrm.append(gene[0])
                    else: chrm.append([])
                n_chrsms.append(chrm)
            #update chrsms
            chrsms=n_chrsms
            #evaluation
            post_scores={self.fitness(i):i for i in n_chrsms}
            post_opt=max(post_scores)
            post_sol=post_scores[post_opt]

            if pre_opt>=post_opt: 
                t+=1
            elif pre_opt<=post_opt:
                pre_opt=post_opt
                pre_scores=post_scores
                pre_sol=post_sol

            if t>500: condition =False
            
            
        ed=time.time()
        return pre_opt,pre_sol,ed-st     