# GAQLA
## 💡 summary
<ul><li><code style="color : Gray">GAQLA 알고리즘은 VRP with Constraints 에 적용가능한 휴리스틱 알고리즘입니다.</code></li><li><code style="color : Gray">GA(유전알고리즘)와 q-labelling algorithm(Exact ESPRC 알고리즘을 변형)으로 이루어진 2-phase 휴리스틱입니다.</code></li><li><code style="color : Gray">예시코드는 Python으로 작성됐습니다.</code></li></ul>
<br>   
<br> 
<p align="center">
<img width="457" alt="image" src="https://github.com/user-attachments/assets/03b13fd0-0193-448a-95ab-5b46622a9384">
<p\>
<p align="center">
Fig 1. flow-chart of GAQLA
<p\>
<br>   
<br> 

## 1. Phase 1 - Paht generation
* 이 단계에서는 가능한 모든 tour를 발견한다.
* ESPRC 문제를 위해 고안된 exact 알고리즘인 labelling 알고리즘을 변형한 q-labelling 알고리즘을 적용했다.
<p align="center">
<img width="457" alt="image" src="https://github.com/user-attachments/assets/744a498e-84af-4f4a-9826-212d9e483eb5">
<p\>
<p align="center">
Fig. flow-chart of CPVP algorithm
<p\>
    
</p> 
<br>   
<br>   
  
    
## 📄 Code

### 0. Main
* 크리티컬 포인트 방문 확률을 최종적으로 계산한다.

```python
def main(criticalpoint, P):
    a,b=agg_heatmap(criticalpoint, P)
    c= CPVP_value(criticalpoint,a,b)
    return c
```
---

### 1. Grid indexing_1
* Grid는 1차원 리스트로 저장된다.
* 1차원 리스트이 인덱스를 2차원 행렬로 변환하여, 실제 그리드가 2차원 상에서 어느 위치에 있을지를 반환한다.

```python
def n_to_coords(num,n=31):
    #사각형의 번호로 몇 행 몇 열에 있는지 반환
    i = num//n
    j = num%n

    return i,j
```
---
### 2. Grid indexing_2
* 특정 좌표가 속해 있는 그리드 인덱스를 반환합니다.
* 인덱스는 1차원 값입니다. 이 1차원 값은 Grid indexing_2 함수에 의해 실제 2차원 인덱스로 변환됩니다.

```python
def fit_point_to_square(point,sofsquare):
    #점이 해당하는 사각형의 인덱스 반환
    for i in range(len(sofsquare)):
        if point[0] >= sofsquare[i][0][0] and point[0] <= sofsquare[i][2][0] and  point[1] >= sofsquare[i][0][1] and point[1] <= sofsquare[i][2][1]:
            return i
```
---
### 3. Grid generation
* Critical point를 중심으로 N X N 크기의 그리드를 생성합니다.
* 그리드 한 칸의 규격은 750X750 m^2 입니다.

```python
def generation_square(squarecenter,n=31):
    #센터를 중심으로 가로,세로 1.5km의 정사각형을 n개의 정사각형으로 분할.
    l1=squarecenter[0]-0.007831555125996204*4 #약0.75km
    ln1=squarecenter[1]-0.009677410125732422*4#약0.75km
    l2=squarecenter[0]+0.007831555125996204*4 
    ln2=squarecenter[1]+0.009677410125732422*4
    square=[[l1,ln1],[l1,ln2],[l2,ln1],[l2,ln2]]
    set_of_unitsqaure=[]
    
    step_of_l=float((l2-l1)/n)
    step_of_ln=float((ln2-ln1)/n)
    for i in range(n):
        for j in range(n):
            temp=[[l1+i*step_of_l,ln1+j*step_of_ln],[l1+i*step_of_l,ln1+(j+1)*step_of_ln],[l1+(i+1)*step_of_l,ln1+(j+1)*step_of_ln],[l1+(i+1)*step_of_l,ln1+j*step_of_ln]]
            set_of_unitsqaure.append(temp)
    return set_of_unitsqaure
```
---
### 4. Generate heatmaps
* GPS 좌표 별로 히트맵을 만든다.
* 기준점은 크리티컬포인트이다.
* 각 그리드에는 히트맵 스코어가 입력되며, 히트맵 스코어는 GPS 좌표와 멀어질수록 작은 값을 지닌다.
* 이차원 배열 형태의 히트맵 스코어를 반환한다.

```python
def generate_heatmap_by_point(point,sofsquare):
    dummy=[[0 for i in range(int(len(sofsquare)**(1/2)))]for j in range(int(len(sofsquare)**(1/2)))]
    #dummy = [[0]*int(math.sqrt(len(sofsquare)))]*int(math.sqrt(len(sofsquare)))
    q=fit_point_to_square(point,sofsquare)
    if q:
        i_,j_=  n_to_coords(q,int(math.sqrt(len(sofsquare))))
        emptiness=True
        x=0
        while emptiness:
            for i in range(i_-x,i_+x+1):
                for j in range(j_-x,j_+x+1):
                    if i >=0 and i< len(dummy) and  j >=0 and j< len(dummy):
                        dummy[i][j]=max(dummy[i][j],100/(math.log(x+1)+0.5))
                        #dummy[i][j]+=100/((x+1)*(x+1))
            x+=1
        
            can=[]
            for i in dummy:
                for j in i:
                    if j == 0:
                        can.append(j)
            if len(can)==0:
                emptiness = False
    return dummy
```

---
### 5. agrregate heatmaps
* 만들어진 히트맵을 하나의히트맵으로 합친다.
* 합쳐진 히트맵의 각 그리드에는 동일한 위치에 저장됐던 각 히트맵들의 스코어를 sum한 값이 입력된다.

```python
def agg_heatmap(squarecenter,P):
    a= generation_square(squarecenter)
    can=[[0 for i in range(int(len(a)**(1/2)))]for j in range(int(len(a)**(1/2)))]
    #can=np.zeros([int(math.sqrt(len(a))),int(math.sqrt(len(a)))])
    for p in P:
        t=generate_heatmap_by_point(p,a)
        if len(t)>0:
            can=[[can[i][j]+t[i][j] for j in range(int(len(a)**(1/2)))]for i in range(int(len(a)**(1/2)))]
    return can,a
```

---

### 6. Calculate CPVP point
* 크리티컬 포인트 방문 확률을 계산한다.
* grid 를 $G$, critical point의 인덱스를 $(i,j)$라 할 때, $CPVP\ =\ G_{ij}/\max{\{\ G\}}$ 

```python
def CPVP_value(critical_point,can,square):
    
    a = can
    b= square #a=heatmap score, b= map
    c=critical_point
    f,p=n_to_coords(fit_point_to_square(c,b))
    m=np.max(a)
    if m == 0:
        val=0
    if m!=0:
        val=a[f][p]/m
    return val

```
