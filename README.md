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
    
---

## 1. Phase 1 - Path generation
* 이 단계에서는 가능한 모든 tour를 발견한다.
* ESPRC 문제를 위해 고안된 exact 알고리즘인 labelling 알고리즘을 변형한 q-labelling 알고리즘을 적용했다.

<br>   
<br> 
<p align="center">
<img width="457" alt="image" src="https://github.com/user-attachments/assets/744a498e-84af-4f4a-9826-212d9e483eb5">
<p\>
<p align="center">
Fig 2. flow-chart of q-labelling algorithm
<p\>
    
</p> 
<br>   
<br>   

## 2. Phase 2 - Solution finding
* 이 단계에서는 전 단계에서 발견한 투어 중 목적함수를 최대화 하는 투어를 선택한다.
* 유전 알고리즘(GA)을 적용했다.
* l-tournament selection와 single-point cross over를 적용했다. fitness는 Objective value이다.

<br>   
<br> 
<p align="center">
<img width="457" alt="image" src="https://github.com/user-attachments/assets/d2b7ebcb-47b0-4339-b059-de2ca44fb000">
<p\>
<p align="center">
Fig 3. flow-chart of GA
<p\>
    
</p> 
<br>   
<br>   
