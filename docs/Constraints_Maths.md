# Constraints formulated as maths equations

*See Problem_Definition.md first !*

- Our university has:
    - A given **r** number of rooms. Each room might be a **special room**.
        - **Special rooms** are rooms with specific furnitures. For instance lab furnitures are in **lab** rooms. **Lab** rooms are considered as a **special room**.
        - Rooms that aren't **special rooms** are refered too as **rooms**.
        - **Amphitheatres** are considered as **special rooms**.

        - Let $r$ be the number of rooms, $r_{special}$ the number of special rooms. We must ensure that:

            $$r\in\mathbb{N} \\  r_{special} \le r$$

    - A given **t** amount of teachers. Each teacher has one or more corresponding subjects he/she can teach.
        - Let $t$ be the number of teachers.

        $$t \in \mathbb{N}$$ 

    - **N** promotions (= year the student is on).
        - Let $N_{promotions}$ be the number of promotions: 
        
            $$N_{promotions} \in \mathbb{N}$$

    - Each promotion has:
        - **n** classes (= group of students).
            - Let $n_{classes}$ be the number of classes: 
            
            $$n_{classes} \in \mathbb{N}$$
            
        - To each class, we assign **s** subjects (= materials) the class has to attend.
            - Let $s$ be the number of subjects. 
                    
            $$s \in \mathbb{N}$$
              
- Each of the **s** subjects has:
    - A fixed number of hours **h** to be completed.

        - Let $h_s$ the number of hours that must be completed as part of this course and $h_{s_a}$ the currently attributed hours for this subject.

        - Let $t_{s_i} , \forall i \in \mathbb{N}$ be a timeslot attributed to subject $s$. $h_{s_a}$ is defined as:

            $$h_{s_a} = \sum_{i=0}^{h_s} t_{s_i}$$
        
        - We must ensure:
            $$h_{s_a} = h_s$$

    - The **h** hours are divided in **online_hours** and **presential_hours**.
    - We need to make sure that **online_hours** <= (30%) * **h**

        - Let $h_{s_o}$ the number of online hours attributed to subject $s$ and $h_{s_p}$ the number of presential hours attributed to subject $s$. We must ensure:

            $$h_{s_a} = h_{s_p}+h_{s_o} \\ h_{s_o} \le 0.30\times h_{s_a}$$
      
- To complete the **h** hours:
    - One course duration is 1h30.
        - Let $t_i$ be an assignated timeslot. We must ensure that:

        $$\frac{\sum_{i=0} t_i}{1.5} = k , k\in\mathbb{N}$$


    - A class can attend as many **courses** as required to attend the **h** hours.

        - Reminder : $h_s$ is the number of hours that must be completed as part of a course. Thus:

        $$h_s \in \mathbb{R}^+$$

    - Some **courses** need to take place in special rooms depending on the **course**'s format. (For example practical works need to be in labs)

        - Let $r_i$ denote a specific room and $s$ denote a course.
        - Define $R_{special}$ as the set of all special rooms, and $S_{special}$ as the set of all courses requiring special rooms.
        - For each course $s\in S_{special}, \exists r_i \in R_{special}$ such that:

        $$s := r_i \Longrightarrow r_i \in R_{special}$$

    - Two different classes can't attend the same **course** in the same **room** on the same **timeslot**
        - Let $T(r_i)$ be the set of timeslots assigned to room $r_i$ and let $S(t_i,r_i)$ be the set of courses assigned to room $r_i$ on timeslot $t_i$ :

        $$\forall t_i \in T(r_i), \left|S(t_i,r_i)\right| \le 1$$

    - An exception is made for **courses** taking place in **amphitheatres**
        - Let $A$ be the set of all amphitheatres.
        - Let $T(r_i \in A)$ be the set of timeslots assigned to room $r_i$, $r_i$ being an amphitheatre.
        - Let $S(t_i,r_i)$ be the set of courses assigned to room $r_i$ on timeslot $t_i$.
        - Let $C$ be the set of classes that need to attend the course in the amphitheatre.

        $$\forall t_i \in T(r_i \in A), \left|S(t_i, r_i)\right| \le len(C)$$

    - One class can't have two **courses** in the same **timeslot**
        - Let $T(c_k)$ be the set of timelsots assigned to class $c_k$.
        - Let $S(t_i,c_l)$ be the set of courses assigned to class $c_k$ on timeslot $t_i$.

        $$t_i \in T(c_k), \left|S(t_i,r_i)\right| \le 1$$
      
- The **courses** can take place in defined **timeslots** each day.
    - **Timeslots** are defined as follows:
        - 08:15 to 09:45
        - 10:00 to 11:30
        - 11:45 to 13:15
        - 13:30 to 15:00
        - 15:15 to 16:45
        - 17:00 to 18:30
        - 18:45 to 20:15
    - No **course** can be scheduled on saturday and thursday afternoon (from 13:30 to 20:15). No **course** ca be scheduled on Sunday.
        - Let $T_{sunday}$ be the set of timeslots on sunday.
        - Let $T_{thursday_{afternoon}}$ be the set of timeslots on thursday afternoon (from 13:30 to 20:15).
        - Let $T_{saturday_{afternoon}}$ be the set of timeslots on saturday afternoon (from 13:30 to 20:15).
        - We define $T_{restricted}$ as $T_{restricted} = \{T_{sunday},  T_{thursday_{afternoon}}, T_{saturday_{afternoon}}\}$
        - Let $T$ be the set of all timeslots.

        $$\forall t_i \in T , t_i \notin T_{restricted}$$

    - Students must have at least one free slot a day. Either 11:45 to 13:15 or 13:30 to 15:00. This is to ensure they can eat.
        - Let $T_{lunch} = \{(11:45, 13:15), (13:30, 15:00) \}$
        - Let $T(c_k)$ be the set of timelsots assigned to class $c_k$.

        $$\forall t_i \in T(c_k): \exists t_i \in T_{lunch}, t_i \notin T(c_k)$$

    - **Courses** can be either **online** or **presential**. Respecting the previous condition regarding total amount of online hours.
    - Certain **courses** may require specific time slots due to logisitcal reasons. (e.g. lab courses requiring 3h sessions, thus, two back-to-back **timeslots**)
        - Let $T_{adjacent} = \{(t_i, t_{i+1})\}$:
        - Let $T(s)$ be the set of timeslots assigned to course $s$. 
        - If $s$ requires 3 hours:

        $$\forall (t_i, t_{i+1}) \in T(s) : (t_i, t_{i+1}) \in T_{adjacent}$$
      
- To take place, each **course** needs:
    - An available room. (= A room where there is no course taking place)
    - A corresponding **class**
    - A **teacher** that can teach the **course**'s subject.
        - The **teacher** must be available. He can't give two courses at the same time.
            - Let $T(t_j)$ be the set of timelsots assigned to teacher $t_j$.
            - Let $S(t_i,c_k)$ be the set of courses assigned to class $c_k$ on timeslot $t_i$.

            $$t_i \in T(t_j), \left|S(t_i,t_j)\right| \le 1$$


        - The **teacher** may have preferred teaching time or days. The **schedule** should try to accomodate these perferences as much as possible.
            - Let $P(t_j)$ the set of preferred timeslots for teacher $t_j$. 
            - Let $T(t_j)$ be the set of timeslots assigned to teacher $t_j$.
            - Given $\forall t_i \in T(t_j)$, minimize:

            $$C_{preferrence} = \sum_{t_i \notin P(t_j)} 1$$

- Room and Resource Allocation:
    - Scheduling must allocate regular or special rooms (e.g., labs or amphitheaters) based on course requirements.
    - Ensure adequate use of room resources while preventing overbooking or misuse of special-purpose spaces.