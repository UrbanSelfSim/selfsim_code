__includes
[
  "Initialization/load-agent.nls"
  "Initialization/initialization.nls"
  "Population Dynamics/Education-model.nls"
  "Population Dynamics/Income-model.nls"
  "Population Dynamics/Birth-model.nls"
  "Population Dynamics/Marriage-model.nls"
  "Population Dynamics/Divorce-model.nls"
  "Population Dynamics/Update-relationship.nls"
  "Population Dynamics/Immigration-model.nls"
  "Population Dynamics/Emigration-model.nls"
  "Population Dynamics/Death-model.nls"
  "Population Dynamics/Network-model.nls"
  "Population Dynamics/Retirement-model.nls"
  "Business Occupier and School Dyanmics/Firm-dynamics.nls"
  "Business Occupier and School Dyanmics/School-dynamics.nls"
  "Business Occupier and School Dyanmics/Businessman-dynamics.nls"
  "Business Occupier and School Dyanmics/Labour-dynamics.nls"
  "Business Occupier and School Dyanmics/Student-dynamics.nls"
  "Land Use/Building-development.nls"
  "Real Estate Market/RLC-RFP.nls"
  "Real Estate Market/FLC-CFP.nls"
  "Real Estate Market/BLC-CFP.nls"
  "Mobility and Accessibility/human-mobility.nls"
  "Output Data/output.nls"
]


extensions [gis py csv profiler array table]

globals
[
  Year

  labor-current ;Number of labor force in the current year
  labor-last ;Number of labor force in the last year

  ;customer flow of businessman
  Ave-Shopping-flow ;Average customer flow to businessmen for shopping in the current year
  Ave-Shopping-flow-last;Average customer flow to businessmen for shopping in the previous year
  Ave-Leisure-flow;Average customer flow to businessmen for leisure in the current year
  Ave-Leisure-flow-last ;Average customer flow to businessmen for leisure in the previous year

  ;average real estate price
  ave-rf-price ;Average purchasing price of residential facilities in the current year
  ave-rf-price-last ;Average purchasing price of residential facilities in the previous year
  ave-rf-rent;Average rent of residential facilities in the current year
  ave-rf-rent-last;Average rent of residential facilities in the previous year
  ave-Cff-rent;Average rent of office (firm) facilities in the current year
  ave-Cff-rent-last;Average rent of office (firm) facilities in the previous year
  ave-cfb-rent;Average rent of commercial (businessman) facilities in the current year
  ave-cfb-rent-last;Average rent of commercial (businessman) facilities in the previous year

  neighborhood ;Defines the spatial range considered as the surrounding area of an agent or facility during the simulation process.

  ;Population Dynamics Model-----------------------------------------------------------------------------------------------------------------------------------------
  ;Parameters of social network model
  P-wgt-age ;Weight assigned to age differences when calculating social similarity
  P-wgt-gen ;Weight assigned to gender differences when calculating social similarity
  P-wgt-inco ;Weight assigned to income group differences when calculating social similarity
  P-wgt-edu ;Weight assigned to education level differences when calculating social similarity
  P-min-net ;threshold of breaking friendship
  P-gro-inco ;Relationship between income and income group
  P-gro-edu ;Relationship between education and education group
  P-gro-age ;Relationship between age and age group

  ;Birth model
  ;Birth-config ; [The maximum eligible age for females childbearing  | The maximum number of children a couple can have]
  P-bir ;Number of people born each year
  P-age-bir
  P-max-bir
  P-bir-decay
  P-bir-coef

  ;Immigration model
  P-imm ;Number of people immigrate each year

  ;Emigration model
  P-emi ;Number of people emigrate each year

  ;Death model
  P-dea ;Total number of deaths per year

  ;Marriage model
  P-mar ;Number of married couples each year
  P-age-mar-male ;minimum legal marriage age for male
  P-age-mar-fem ;minimum legal marriage age for female

  ;Divorce model
  P-div ;Number of divorced couples each year

  ;Income model
  P-cha-inco ;income change
  P-inc-min ;Predefined minimum income threshold

  ;Retirement model
  P-age-ret-male ;Male retirement age
  P-age-ret-fem ;Female retirement age
  P-inco-ret ;The ratio of post retirement salary to pre retirement salary

  ;education and school parameters
  P-pro-fur ;probability of pursuing further education after completing the current education level at each education level [probability of education = 0 | probability of education = 1 | ...]
  P-edu-fur ;Transition probability matrix element; probability that an agent at education level i advances to level j [[edu_i | edu_j | probability] [edu_i | edu_j | probability]]
  P-edu-sch ;records the schools and required study duration associated with each education level  [[education | school | duration]


  ;Business occupier and school dynamics model--------------------------------------------------------------------------------------------------------------------------------------------------------------

  ;Firm birth model
  B-pro-lab ;The proportion of labor force growth that gives rise to new start-ups
  B-pro-firm-exi ;The proportion of existing firms that gives rise to new start-ups
  B-mean-firm
  B-dif-firm

  ;Firm growth model
  B-coe-size-firm ;The coefficient for the size effect of the firm growth
  B-coe2-size-firm ;The coefficient for the square size effect of the firm growth
  B-coe-age-firm ;The coefficient for the age effect of the firm growth
  B-coe-acc ;The coefficient for the accessibility effect of the firm growth
  B-low-firm ;The lower threshold of the growth rate for firms growth
  B-up-firm ;The upper threshold of the growth rate for firms growth

  ;Firm closure model
  B-clo-year-firm ;The number of consecutive years considered when evaluating firm closure
  B-SF-firm ;The scaling factor used to adjust the closure threshold of the firm’s growth rate

  ;Businessman flow calculation
  B-coe-liv-sho	 ;The coefficient of the residential agents' influence on the flow (shopping)
  B-coe-liv-lei	;The coefficient of the residential agents' influence on the flow (leisure)
  B-coe-we-sho	;The coefficient of the working/education agents' influence on the flow (shopping)
  B-coe-we-lei;The coefficient of the working/education agents' influence on the flow (leisure)

  ;Businessman birth model
  B-coe-sho ;The adjustment coefficient used to control the proportion of the increase in average customer flow per businessman agent that is converted into the number of new businessman agents (shopping)
  B-coe-lei ;;The adjustment coefficient used to control the proportion of the increase in average customer flow per businessman agent that is converted into the number of new businessman agents (leisure)
  B-mean-bus
  B-dif-bus

  ;Businessman growth model
  B-up-busi ;The upper threshold of the growth rate for the businessman agent growth
  B-low-busi ;The lower threshold of the growth rate for the businessman agent growth
  B-coe-size-busi ;The coefficient for the size effect of the businessman agent growth
  B-coe2-size-busi	;The coefficient for the square size effect of the businessman agent growth
  B-coe-age-busi ;The coefficient for the customer age effect of the businessman agent growth	
  B-coe-flow ;The coefficient for the customer flow effect of the businessman agent growth

  ;Businessman closure model
  B-SF-busi	 ;The scaling factor used to adjust the closure threshold of the businessman agent’s growth rate
  B-clo-year-busi ;The number of consecutive years considered when evaluating businessman agent closure

  ;School dynamics model
  B-coe-sch	;The adjustment coefficient used to control the proportion of the increase in the number of students that is converted into the number of new schools
  B-pro-bir-sch ;The proportion of capacity used to determine whether to add new schools
  B-coe-dis-sch ;The distance decay coefficient reflecting how distance reduces the likelihood of assignment of student
  B-coe-lab-sch ;the student-to-employee ratio [ratio of school 1 | ratio of school 2 | ratio of school 3]
  B-sch-clo ;The closure threshold for the school
  B-stu-last ;number of students in each type of schools [number of student in school 1 | ......] (last year)
  B-stu-cur ;number of students in each type of schools [number of student in school 1 | ......] (current year)

  ;parameters of real estate market model---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ;residential location choice
  R-can-res ;maximum number of candidate residential facilities
  R-neg-num-res ;The upper threshold for the number of residential negotiations
  R-neg-pri-res ;The threshold for the residential price change rate
  R-loss ;loss effect
  R-move-owning ;The threshold for the number of flexible triggers to decide whether to rent a new residence
  R-move-renting ;The threshold for the number of flexible triggers to decide whether to purchase a new residence
  R-pro-inc-pri ;The proportion for the price increase of the residence
  R-pro-dec-pri	 ;The proportion for the selling price decrease of the residence
  R-inc-pri	;The threshold for the selling price increase of the residence
  R-dec-pri ;The threshold for the selling price decrease of the residence
  R-wgt-acc ;The weight for the accessibility of the residence
  R-wgt-pri ;The weight for the price of the residence
  R-aff-owning	;affordability of purchasing a residence
  R-exp-hou-owing ;The threshold for the score of the candidate residence that a householld can accept
  R-pro-inc-rent ;The proportion for the rent increase of the residence
  R-pro-dec-rent	;The proportion for the rent decrease of the residence
  R-inc-rent	;The threshold for the rent increase of the residence
  R-dec-rent	;The threshold for the rent decrease of the residence
  R-wgt-acc-rent	;The weight for the accessibility of the residence
  R-wgt-pri-rent	;The weight for the price of the residence
  R-aff-rent	;affordability of renting a residence
  R-exp-hou-rent ;The threshold for the score of the candidate residence that a householld can accept

  ;firm location choice
  R-coe-rent-firm	 ;The weight parameter for the rent of the candidate commercial facility – firms
  R-coe-acc-firm	;The weight parameter for the accessibility of the candidate commercial facility – firms
  R-coe-agg-firm	;The weight parameter for the agglomeration degree of the candidate commercial facility – firms
  R-coe-space-firm	;The proportion for the rent increase of the commercial facility - firms
  R-move-firm ;The utility threshold for determining whether a firm needs to move.
  R-wgt-rent-CFF ;The weight parameter for the rent of the candidate commercial facility – firms
  R-wgt-acc-CFF	;The weight parameter for the accessibility of the candidate commercial facility – firms
  R-wgt-agg-CFF	;The weight parameter for the agglomeration of the candidate commercial facility – firms
  R-exp-firm ;The threshold for the score of the candidate CFF that a firm can accept
  R-pro-inc-CFF	 ;The proportion for the rent increase of the commercial facility - firms
  R-pro-dec-CFF	 ;The proportion for the rent decrease of the commercial facility - firms
  R-inc-CFF ;The threshold for the rent increase of the commercial facility - firms
  R-dec-CFF	;The threshold for the rent decrease of the commercial facility - firms
  R-up-CFF	;The upper limit of rent of CFF
  R-low-CFF ;The lower limit of rent of CFF
  R-can-CFF ;maximum number of candidate commercial faclity for firms
  R-neg-num-CFF ;The upper threshold for the number of negotiations of commercial faclity for firms
  R-neg-rent-CFF ;The threshold for the commercial facility rent change rate -firm

  ;businessman location choice
  R-pro-inc-CFB ;The proportion for the rent increase of the commercial facility - businessman
  R-pro-dec-CFB	;The proportion for the rent decrease of the commercial facility - businessman
  R-inc-CFB	;The threshold for the rent decrease of the commercial facility - businessman
  R-dec-CFB		;The threshold for the rent decrease of the commercial facility - businessman
  R-up-CFB;The upper limit of rent of CFF
  R-low-CFB;The lower limit of rent of CFF
  R-wgt-rent-CFB	;The weight parameter for the rent of the candidate commercial facility – businessman
  R-wgt-agg-CFB	;The weight parameter for the agglomeration of the candidate commercial facility – businessman
  R-wgt-flow-CFB	;The weight parameter for the customer flow of the candidate commercial facility – businessman
  R-exp-busi;The threshold for the score of the candidate CFB that a businessman can accept
  R-can-CFB ;maximum number of candidate commercial faclity for businessmen
  R-neg-num-CFB ;The upper threshold for the number of negotiations of commercial faclity for businessmen
  R-neg-rent-CFB ;The threshold for the CFB rent change rate

  ;Real estate transaction volume
  res-purchase-transaction
  res-rent-transaction
  CFF-rent-transaction
  CFB-rent-transaction

  ;Land use model-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  L-coe-cap ;The coefficient that determines the relationship between the additional activity facility capacity and the demand capacity
  L-det-new ;The threshold of determine whether to add new facility capacity

  ;Human mobility model-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ;distance distribution of
  H-sho-loc-weekday ;distribution of the location of shopping activity happen on weekday[<2km 2-5km 5-10km 10-20km >20km]
  H-sho-loc-weekend ;distribution of the location of shopping activity happen on weekend[<2km 2-5km 5-10km 10-20km >20km]
  H-lei-loc-weekday;distribution of the location of leisure activity happen on weekday[<2km 2-5km 5-10km 10-20km >20km]
  H-lei-loc-weekend;distribution of the location of leisure activity happen on weekend[<2km 2-5km 5-10km 10-20km >20km]

  ;Distribution of travel mode choices by distance (for vehicle owner and non-vehicle owner)
  ;Transport mode : Bus Private_vehicle Subway Taxi Two_wheels Walking For-Hire Vehicle
  H-mode-vo-weekday ;[[prob-Bus-2km | prob-Private_vehicle-2km | prob-Subway-2km |prob-Taxi-2km |prob-Two_wheels-2km | prob-Walking-2km | probFor-Hire Vehicle] [prob of 2-5km] [prob of 5-10km] [prob of 10-20km] [prob of > 20km]]
  H-mode-vo-weekend
  H-mode-nvo-weekday
  H-mode-nvo-weekend

]

breed [People Person]
breed [Households Household]
breed [RFs RF]
breed [Schools School]
breed [Firms Firm]
breed [CFBs CFB] ;commercial facilities
breed [Businessmen Businessman] ;commercial establishment
breed [CFFs CFF] ;office building

undirected-link-breed [couples couple]
undirected-link-breed [parents parent]
undirected-link-breed [grapas grapa]
undirected-link-breed [friends friend]
undirected-link-breed [cpurchases cpurchase] ;candidate residences to purchase
undirected-link-breed [crents crent] ;candidate residences to rent
undirected-link-breed [rents rent]
undirected-link-breed [purchases purchase]
undirected-link-breed [students student]
undirected-link-breed [employees employee]

;shopping and leisure
undirected-link-breed [shoppings shopping]
undirected-link-breed [leisures leisure]

undirected-link-breed [cfrents cfrent] ;candidate commercial facility (firm)
undirected-link-breed [cbrents cbrent] ;candidate commercial building (businessman)

patches-own
[
  random-n
  centroid
  ID
  admin ;determine whether the patch falls into the study area
  dem-RF ;demand-residences demand of residential building in this patch (the higher the demand, the more likely to develop a new residential building
  dem-CFF
  dem-CFB
  dem-school
]

households-own
[
  hhd
  hhd-size
  hhd-income
  res ;residence ID
  flexible ;number of accumulated flexible triggers
  mandatory ;mandatory trigger 0- have no mandatory trigger; 1- have mandatory trigger
  residence-size ;current residence size
  residence-cost ;current residence cost
  move ;determine whether move house this year
  acc-current
  acc-candidate
  Long
  Lat
]

people-own
[
  pid ;person ID
  hhd ;household ID
  relationship ;1 housholder 2 spouse of householder 3 son/daughter of householder 4 parents of householder 5 parents of spouse 6 Grandchildren of householder 7 grandparents of housholder 8 maternal grandparents of householder 9 spouse's grandparents 10 maternal grandparents of spouse 11 siblings of householder 12 other 13Daughter-in-law Son-in-law
  age ;The specific age starting from 0.
  age-group ;The grouping rules are specified in the configuration file.
  gender ;0-female; 1-male
  income ; The specific income starting from 0.
  income-group ;The grouping rules are specified in the configuration file.

  ;education related attributes
  education ;The specific education, start from 0 (preschool)
  education-group ;The grouping rules are specified in the configuration file.
  edu-year ;Years of study at the current school
  edu-year-required ;The duration of study required for each level of education.

  status ;1-students or preschoolers 2-employees 3-unemployees 4-retirees

  ;social network attributes
  max-friend ;The maximum number of friends the person can have.
  min-friend ;The minimum number of friends one must have.
  Similarity ; It is used to store the degree of similarity between one person agent and another person agent.


  ;residence/work and study/shopping/leisure attributes
  district ;district
  livelong ;longitude of residential location
  livelat  ;latitude of residentia
  welong  ;longitude of work or education place
  welat ;latitude of work or education place


  ;Accessibility
  Acc-current
  Acc-candidate

  chain-weekday ;It is used to store the activity chain of this person agent on a typical weekday, with the data format as follows: ["home" "work" "leisure" "home"]
  chain-weekend;It is used to store the activity chain of this person agent on a typical weekend, with the data format as follows: ["home" "leisur" "home"]

  plan-weekday ;It is used to store the complete daily plan of this person agent on a typical weekday,  with the data format as follows:[["home" "residence 1" 140.36 36.97 6000 "bus"] [] [] []]   [activity type | facility id | long | lat | duration | transporation mode to next location]
  plan-weekend ;It is used to store the complete daily plan of this person agent on a typical weekend, with the data format as follows:
  vir-plan-weekday ; It is used to generate a virtual daily plan that used to calculate accessibility of residential facility candidates
  vir-plan-weekend

  ;commuting distance
  dis-cur
  dis-can

  vehicle-owner
]

RFs-own
[
  rid ;residential building ID
  available-space
  capacity
  ResPrice ;sale price per unit
  Resrent ;rent per unit
  purchaser-income ;average income of purchasers in this residential building
  renter-income ;average income of renters in this residential building
  long  ;longitude
  lat  ;latitude
  att-price ;attractiveness to candidate purchasers
  att-rent ;attractiveness to candidate renters
  surrounding-purchase ;purchasings of residential residences within N km
  surrounding-rent ;rents of residential residences within N km
]

firms-own
[
  FID  ;ID of firm
  Age ;age of firm

  emp-req ;required number of employees
  firm-size ;the number of employees
  closure ;for how many years the firm's growth rate of capacity is lower than the closure threshold

  office-size
  office-cost ;Office rent for this year
  office-cost-last ;office rent of last year
  office-cost-next ;office rent of next year
  agg ;agglomeration
  agg-last ;agglomeration last year
  acc ;accessibility
  acc-last ;accessibility last year
  location-choice ;Should the company move to another office building
  Long  ;longitude
  Lat  ;latitude
  UMove ;Utility of move to another office building. If Umove greater than a threshold, the firm will move.

  dis-can
]

CFFs-own
[
  CFFID
  CFFrent ;rent of capacity
  capacity
  available-space
  long ;longitude
  lat ;latitude
  attractiveness ;attractiveness of CFF
  CFFrent-max ;The maximum value that rent can rise to
  CFFrent-min ;The minimum value that rent can fall to
  agg
]

;commercial building
CFBs-own
[
  CFBID ;ID
  Long
  Lat
  Capacity
  Available-space
  CFBRent ;rent
  CFBrent-max ;The maximum rent of the CFB can rise to in this simulation year
  CFBrent-min ;The minimum rent of the CFB can decrease to in this simulation year
  flow ;The customer flow
  Agg-shopping ;agglomeration of the businessmen for shopping, which is the sum of capacity of surrouding businessmen for shopping
  Agg-leisure ;agglomeration of the businessmen for leisuring, which is the sum of capacity of surrouding businessmen for leisuring
  attractiveness ;attractiveness
  my-distance ;used to record information of daily plan updating
]

Businessmen-own
[
  BID
  Btype ;1- place for shopping; 2- place for leisuring
  Space ;Space occupied, which determines the probability a consumer consuming here
  Long ;longitude
  Lat ;latitude
  location-choice ;whether need to choose a location
  Busi-size ;number of employees
  emp-req ;number of employees required
  flow ;Customner flow
  age
  closure ;number of consecutive years the growth rate reached the closure standard
  dis-can

  ; utility of businessman growth
  Usize
  Usizesq
  Uage
  Uflow
]

schools-own
[
  SchID ;ID of school
  Long ;longitude
  lat ;latitude
  Stype ;Types of school, defined in configuration file "Education School.csv"
  capacity ;The recommended maximum student capacity for each school, which can still accommodate additional students even if the limit is reached.
  available-space; number of available spots for students
  School-size ; number of employees
  emp-req ;number of employees required
  Num-student ;number of students in the school
  dis-can
]

shoppings-own
[
  daytype ; Record the time of activity 1- weekday 2- weekend
]

leisures-own
[
  daytype ; Record the time of activity 1- weekday 2- weekend
]

to setup
  clear-all
  setup-python
  set year base-year
  load-agent
  initialization
  print "initialization finished"
  if social-network
  [
    generate-network
    print "network finished"
  ]
  ask links [hide-link]
  reset-ticks
  export-world (word year ".csv")
end

to setup-python
  py:setup py:python
  (py:run
    ; dbscan python packages
    "from sklearn.cluster import DBSCAN"
    "from sklearn.datasets import make_blobs"
    ; p-median python packages
    "from itertools import product"
;    "from gurobipy import *"
    "from pulp import *"
    "import numpy as np"
    "from math import sqrt"
    "import random"
    "import matplotlib.pyplot as plt"
    "from scipy.optimize import curve_fit"
    "random.seed(0)"
    "import os"
    "from scipy.stats import gamma"
    "import pandas as pd"
    "from sklearn.ensemble import RandomForestRegressor"
    "from sklearn.ensemble import RandomForestClassifier"
    "from io import StringIO"
  )
end

to go
  set labor-last count people with [status = 2 or status = 3]
;  set transaction-rent 0 set transaction-purchase 0
  set year year + 1

  ;Population dynamics model
  ask people [set age age + 1] ;age model
  income-model
  birth-model
  death-model
  education-model
  retirement-model
  marriage-model
  print count households with [count people with [hhd = [hhd] of myself and relationship = 1] = 0]
  divorce-model
  emigration-model
  immigration-model
  if social-network [update-friend]

  ;Business occupier and school dynamics model
  firm-dynamics-model
  school-dynamics-model
  Businessman-dynamics-model
  labour-dynamics

;  ;Residential location choice and real estate price model
  RLC-REP
  FLC-CFP
  BLC-CFP

  building-development-model
  output-data
  ask links [hide-link]
  tick
  export-world (word year ".csv")
end
@#$#@#$#@
GRAPHICS-WINDOW
618
10
1009
402
-1
-1
2.38
1
10
1
1
1
0
0
0
1
-80
80
-80
80
1
1
1
ticks
30.0

BUTTON
23
21
89
54
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
101
22
164
55
NIL
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
23
102
159
147
Number of Schools
count schools
17
1
11

MONITOR
21
173
136
218
Number of firms
count firms
17
1
11

MONITOR
1181
30
1305
75
Number of people
count people
17
1
11

MONITOR
632
26
689
71
Year
Year
17
1
11

MONITOR
19
254
162
299
Number of Businessmen
count Businessmen
17
1
11

MONITOR
1327
30
1458
75
Number of couples
count couples
17
1
11

MONITOR
171
102
309
147
Number of students
count people with [status = 1]
17
1
11

MONITOR
1485
32
1643
77
Number of Unemployees
Count people with [status = 3]
17
1
11

MONITOR
1181
85
1325
130
Number of employees
count people with [status = 2]
17
1
11

MONITOR
1339
86
1477
131
Number of retirees
count people with [status = 4]
17
1
11

TEXTBOX
60
77
486
103
---------------------School Dynamics Model-------------------------
12
0.0
1

TEXTBOX
638
419
1098
445
---------------------Real Estate Market Model-------------------------
12
0.0
1

TEXTBOX
84
234
486
260
-----------Commercial Building and Commercial Establishment-------
12
0.0
1

TEXTBOX
61
154
434
172
---------------------Firm Dynamics Model----------------------
12
0.0
1

SWITCH
1016
105
1158
138
Social-Network
Social-Network
1
1
-1000

BUTTON
175
22
289
55
NIL
setup-python
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

PLOT
1179
150
1680
445
Social Demographic Attributes
year
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Male" 1.0 0 -16777216 true "" "plot count people with [gender = 1]"
"Female" 1.0 0 -7500403 true "" "plot count people with [gender = 0]"
"Students" 1.0 0 -2674135 true "" "plot count people with [status = 1 and age >= 3]"
"Employee" 1.0 0 -955883 true "" "plot count people with [status = 2]"
"Retiree" 1.0 0 -6459832 true "" "plot count people with [status = 4]"
"Education-HighSchool or Below" 1.0 0 -13840069 true "" "plot count people with [education <= 5]"
"Education-College" 1.0 0 -14835848 true "" "plot count people with [education = 6]"
"Education-Bachelor" 1.0 0 -11221820 true "" "plot count people with [education = 7 or education = 8]"
"Education-Master or PHD" 1.0 0 -13791810 true "" "plot count people with [education >= 9]"
"People" 1.0 0 -13345367 true "" "plot count people"
"Unemployee" 1.0 0 -8630108 true "" "plot count people with [status = 3]"
"IndividualMonthlyIncome-0~5k" 1.0 0 -1184463 true "" "plot count people with [status = 2 and income <= 5000]"
"IndividualMonthlyIncome-5~10k" 1.0 0 -10899396 true "" "plot count people with [status = 2 and income > 5000 and income <= 10000]"
"IndividualMonthlyIncome-10~15k" 1.0 0 -5825686 true "" "plot count people with [status = 2 and income > 10000 and income <= 15000]"
"IndividualMonthlyIncome-15~20k" 1.0 0 -2064490 true "" "plot count people with [status = 2 and income > 15000 and income <= 20000]"
"IndividualMonthlyIncome-Above20k" 1.0 0 -16777216 true "" "plot count people with [status = 2 and income > 20000]"
"HouseholdIncome" 1.0 0 -16777216 true "" "plot mean [hhd-income] of households"

INPUTBOX
529
16
604
76
Base-Year
2018.0
1
0
Number

CHOOSER
1016
12
1154
57
DailyPlan
DailyPlan
"Simple" "Typical" "Full"
0

MONITOR
317
103
434
148
School Capacity
sum [capacity] of schools
17
1
11

MONITOR
601
446
725
491
RF rental volume
res-rent-transaction
17
1
11

MONITOR
738
446
855
491
RF sales volume
res-purchase-transaction
17
1
11

MONITOR
867
446
991
491
RF average price
ave-rf-price
17
1
11

MONITOR
1005
445
1122
490
RF average rent
ave-RF-rent
17
1
11

MONITOR
601
510
732
555
CFF rental volume
CFF-rent-transaction
17
1
11

MONITOR
744
510
868
555
CFF avearga rent
ave-cff-rent
17
1
11

MONITOR
877
510
1008
555
CFB rental volume
CFB-rent-transaction
17
1
11

MONITOR
1012
510
1136
555
CFB average rent
ave-CFB-rent
17
1
11

TEXTBOX
1203
10
1714
62
----------------------Population Dynamics Model----------------------
12
0.0
1

MONITOR
447
103
598
148
Employees of schools
sum [school-size] of schools
17
1
11

MONITOR
157
173
295
218
Employees of firms
sum [firm-size] of firms
17
1
11

MONITOR
174
253
387
298
Employees required by businessmen
sum [emp-req] of businessmen
17
1
11

MONITOR
394
251
549
296
Employees of businessmen
sum [count in-employee-neighbors] of businessmen
17
1
11

MONITOR
21
306
248
351
Average customer flow (leisure)
ave-leisure-flow
17
1
11

MONITOR
257
306
491
351
Average customer flow (shopping)
ave-shopping-flow
17
1
11

MONITOR
603
574
754
619
RF capacity
sum [capacity] of rfs
17
1
11

MONITOR
763
575
852
620
RF capacity
sum [capacity] of RFs
17
1
11

MONITOR
870
577
1021
622
CFF capacity
sum [capacity] of cffs
17
1
11

MONITOR
1036
575
1180
620
CFF available space
sum [available-space] of CFFs
17
1
11

MONITOR
603
630
754
675
CFB initial capacity
sum [capacity] of CFBs
17
1
11

MONITOR
763
630
901
675
CF available sapce
sum [available-space] of CFBs
17
1
11

BUTTON
299
21
417
54
Parameter Setting
read-settings
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SWITCH
1017
65
1156
98
Export-Attractiveness
Export-Attractiveness
0
1
-1000

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="experiment" repetitions="1" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles</metric>
    <enumeratedValueSet variable="W-shop-rent">
      <value value="0.24"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-firm-loc-rent">
      <value value="-0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-growth-upper">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-rent-afford">
      <value value="0.6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Base-Year">
      <value value="2018"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-OB-increase">
      <value value="1.97"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Loss">
      <value value="1.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Max-CB-rent">
      <value value="0.84"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-income">
      <value value="0.24"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-growth-sizesq">
      <value value="-0.05"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-gender">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-res-rent-acc">
      <value value="0.7"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-firm-move">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-purchase-afford">
      <value value="0.6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-closure">
      <value value="1.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-CB-increase">
      <value value="9.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-school-decrease">
      <value value="0.55"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-shop-traffic">
      <value value="0.19"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-res-purchase-price">
      <value value="0.6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-friend-break">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="DailyPlan">
      <value value="&quot;Simple&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-Move-acc">
      <value value="-0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-res-purchase-acc">
      <value value="0.4"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Rent-prospect">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-firm-loc-agg">
      <value value="0.7"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Social-Network">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Firm-prospect">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-flexible-purchase">
      <value value="7"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-res-rent-price">
      <value value="0.3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Purchase-prospect">
      <value value="-0.01"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-growth-lower">
      <value value="-0.15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Max-num-residences">
      <value value="7"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-OB-decrease">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-growth-age">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-move-agg">
      <value value="-0.09"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-firm-loc-acc">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-age">
      <value value="0.41"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-Move-rent">
      <value value="0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-flexible-rent">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-growth-size">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-school-increase">
      <value value="0.7"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="Min-CB-rent">
      <value value="-0.5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-shop-agg">
      <value value="0.24"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-CB-decrease">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="T-school-birth">
      <value value="0.7"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-move-space">
      <value value="0.55"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-growth-acc">
      <value value="-0.05"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="W-education">
      <value value="0.2"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
