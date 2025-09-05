__includes
[
  "Initialization/load-agent.nls"
  "Initialization/initialize-household-relationship.nls"
  "Initialization/Setup-python.nls"
  "Initialization/Read-settings.nls"
  "Initialization/Initialize-daily-plan.nls"
  "Initialization/Initialize-agent-attributes.nls"
  "Population Dynamics/People-attributes.nls"
  "Population Dynamics/Education-model.nls"
  "Population Dynamics/Income-model.nls"
  "Population Dynamics/Birth-model.nls"
  "Population Dynamics/Marriage-model.nls"
  "Population Dynamics/Divorce-model.nls"
  "Population Dynamics/Update-relationship.nls"
  "Population Dynamics/Immigration-model.nls"
  "Population Dynamics/Emigration-model.nls"
  "Population Dynamics/Death-model.nls"
  "Population Dynamics/SocNet-model.nls"
  "Population Dynamics/Retirement-model.nls"
  "Population Dynamics/Output-population.nls"
  "Business Occupier and School Dyanmics/Firm-dynamics.nls"
  "Business Occupier and School Dyanmics/School-dynamics.nls"
  "Business Occupier and School Dyanmics/Businessman-dynamics.nls"
  "Business Occupier and School Dyanmics/Labour-dynamics.nls"
  "Business Occupier and School Dyanmics/Student-dynamics.nls"
  "Business Occupier and School Dyanmics/Output-busisiness-school.nls"
  "Land Use/Act-fac-dev.nls"
  "Land Use/Tra-fac-dev.nls"
  "Real Estate Market/Res-loc-cho.nls"
  "Real Estate Market/Fir-loc-cho.nls"
  "Real Estate Market/Bus-loc-cho.nls"
  "Real Estate Market/Output-real.nls"
  "Human Mobility/human-mobility.nls"
]


extensions [gis py csv profiler array table web]

globals
[
  Year
  DailyPlan
  Social-network
  Pop-output
  Bus-output
  Rea-output
  Lan-output
  Dai-output
  Complex-acc
  Route

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
  P-decay-bir ;Decay rate associated with the remaining fertility potential of a female agent.
  P-coe-bir ;Coefficient representing the influence of remaining fertility potential on birth probability.

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
  P-min-inco ;Predefined minimum income threshold

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
  B-mean-firm ;The mean of the normal distribution used to generate the initial size of new firms.
  B-std-firm ;The standard deviation of the normal distribution used to generate the initial size of new firms.

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
  B-coe-bir-busi-sho ;The adjustment coefficient used to control the proportion of the increase in average customer flow per businessman agent that is converted into the number of new businessman agents (shopping)
  B-coe-bir-busi-lei ;;The adjustment coefficient used to control the proportion of the increase in average customer flow per businessman agent that is converted into the number of new businessman agents (leisure)
  B-mean-busi ;The mean of the normal distribution used to generate the initial size of new businessman agents.
  B-std-busi ;The standard deviation of the normal distribution used to generate the initial size of new businessman agents.

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
  R-move-pur ;The threshold for the number of flexible triggers to decide whether to rent a new residence
  R-move-rent ;The threshold for the number of flexible triggers to decide whether to purchase a new residence
  R-up-pri-RF	 ;The upper limit of price of  residential facilities
  R-low-pri-RF	;The lower limit of price of  residential facilities
  R-up-rent-RF ;The upper limit of rent of  residential facilities
  R-low-rent-RF	 ;The lower limit of rent of  residential facilities
  R-pro-inc-pri ;The proportion for the price increase of the residence
  R-pro-dec-pri	 ;The proportion for the selling price decrease of the residence
  R-inc-pur	;The threshold for the selling price increase of the residence
  R-dec-pur ;The threshold for the selling price decrease of the residence
  R-wgt-acc-pur ;The weight for the accessibility of the residence
  R-wgt-pri-pur ;The weight for the price of the residence
  R-aff-pur	;affordability of purchasing a residence
  R-exp-hou-pur ;The threshold for the score of the candidate residence that a householld can accept
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
  R-err-mean-firm	 ;Mean of the normally distributed error term for CFF utility calculation.
  R-err-std-firm	;Standard deviation of the normally distributed error term for CFF utility calculation.


  ;businessman location choice
  R-pro-inc-CFB ;The proportion for the rent increase of the commercial facility - businessman
  R-pro-dec-CFB	;The proportion for the rent decrease of the commercial facility - businessman
  R-inc-CFB	;The threshold for the rent decrease of the commercial facility - businessman
  R-dec-CFB		;The threshold for the rent decrease of the commercial facility - businessman
  R-max-rent-CFB;The upper limit of rent of CFF
  R-min-rent-CFB;The lower limit of rent of CFF
  R-wgt-rent-CFB	;The weight parameter for the rent of the candidate commercial facility – businessman
  R-wgt-agg-CFB	;The weight parameter for the agglomeration of the candidate commercial facility – businessman
  R-wgt-flow-CFB	;The weight parameter for the customer flow of the candidate commercial facility – businessman
  R-exp-busi;The threshold for the score of the candidate CFB that a businessman can accept
  R-can-CFB ;maximum number of candidate commercial faclity for businessmen
  R-neg-num-CFB ;The upper threshold for the number of negotiations of commercial faclity for businessmen
  R-neg-rent-CFB ;The threshold for the CFB rent change rate

  ;labor-dynamics
  B-coe-dis-lab ;The coefficient related to gravity model of job choice


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

  M-CF-busi ;represents the number of candidate commercial facilities for business agents.

  ;Accessibility Model
  A-rte ; Detour Index of [Private_vehicle | Two_wheels | Walk | Taxi | For-hire_vehicle | Subway | Bus]
  A-v ;Speed of each transport mode. kmh [Private Vehicle | Two_wheel | Walk | Taxi | For-Hire Vehicle | Subway | Bus]

]

breed [People Person]
breed [Households Household]
breed [RFs RF]
breed [Schools School]
breed [Firms Firm]
breed [CFBs CFB] ;commercial facilities
breed [Businessmen Businessman] ;commercial establishment
breed [CFFs CFF] ;office building
breed [TFs TF] ;transport facility

undirected-link-breed [Spouses Spouse]
undirected-link-breed [parents parent]
undirected-link-breed [grapas grapa]
undirected-link-breed [friends friend]
undirected-link-breed [cpurchases cpurchase] ;candidate residences to purchase
undirected-link-breed [crents crent] ;candidate residences to rent
undirected-link-breed [rents rent]
undirected-link-breed [purchases purchase]
undirected-link-breed [students student]
undirected-link-breed [employees employee]
undirected-link-breed [assigns assign]

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
  pdistrict
  dem-RF ;demand-residences demand of residential building in this patch (the higher the demand, the more likely to develop a new residential building
  dem-CFF
  dem-CFB
  dem-school
]



to setup
  clear-all
  setup-python
  set year base-year
  read-settings
  load-agent
  initialize-relationship
  initialize-daily-plan
  initialize-agent-attributes
  if social-network = 1
  [
    generate-network
    print "network finished"
  ]
  ask links [hide-link]
  reset-ticks
  let filefolder (word "Output Data/" year)
  let filename (word "NetlogoSim" year ".csv")
  py:set "filename" filename
  clear-file filefolder filename
  export-world (word "Output Data/" year "/NetlogoSim" year ".csv")

  let src_folder (word "Scenarios/" study-area "/Settings")
  let dst_root "Output Data"
  py:set "src_folder" src_folder
  py:set "dst_root" dst_root
  (py:run
    "dst_folder = os.path.join(dst_root, 'Settings')"
    "if os.path.exists(dst_folder):"
    "    shutil.rmtree(dst_folder)"
    "shutil.copytree(src_folder, dst_folder)"
  )

  let dailyplan_file (word "Scenarios/" study-area "/Daily Plan/DailyPlan.xml")
  let dst_file (word "Output Data/DailyPlan.xml")
  py:set "dailyplan_file" dailyplan_file
  py:set "dst_file" dst_file
  (py:run
    "if os.path.exists(dst_file):"
    "    os.remove(dst_file)"
    "shutil.copy2(dailyplan_file, dst_file)"
  )
end

to go
  setup-python
  reset-timer
  set labor-last count people with [status = 2 or status = 3]
  set year year + 1

  ;Population dynamics model
  ask people [set plan-changed 0]
  ask people [set age age + 1] ;age model
  income-model
  birth-model
  death-model
  education-model
  retirement-model
  marriage-model
  print (word "Color = black: " count people with [color = black])
  check-item
  divorce-model
  print (word "Color = black: " count people with [color = black])
  check-item
  emigration-model
  immigration-model
  print (word "Color = black: " count people with [color = black])
  check-item
  if social-network = 1 [update-friend]
  output-population


  ;Business occupier and school dynamics model
  firm-dynamics-model
  print (word "Color = black: " count people with [color = black])
  check-item
  output-firm
  school-dynamics-model
  print (word "Color = black: " count people with [color = black])
  check-item
  output-school
  Businessman-dynamics-model
  print (word "Color = black: " count people with [color = black])
  check-item
  output-businessman
  labour-dynamics
  check-item

;  ;Residential location choice and real estate price model
  res-loc-cho
  check-item
  fir-loc-cho
  check-item
  bus-loc-cho
  check-item

  activity-facility-development-model

  Year-End-Output
  ask links [hide-link]
  tick
  let filefolder (word "Output Data/" year)
  let filename (word "NetlogoSim" year ".csv")
  py:set "filename" filename
  clear-file filefolder filename
  export-world (word "Output Data/" year "/NetlogoSim" year ".csv")
  print (word "Calculation time: " timer " seconds.")
end

to clear-file [folder file]
  py:set "filefolder" folder
  py:set "filename" file
  (py:run
    "os.makedirs(filefolder, exist_ok=True)"
    "root_dir = os.getcwd()"
    "for root, dirs, files in os.walk(root_dir):"
    "  for file in files:"
    "    if file == filename:"
    "        file_path = os.path.join(root, file)"
    "        os.remove(file_path)"
  )
end

to check-item
  ask people with [length plan-weekday > 0]
  [
    let num-act length plan-weekday
    let i 0
    while [i < num-act - 2]
    [
      let activity item i plan-weekday
      if length activity != 6 [print (word "PID = " PID " Wrong plan-weekday: " plan-weekday)]
      set i i + 1
    ]
  ]

  ask people with [status = 3 or status = 4]
  [
    let num-act length chain-weekday
    let i 0
    while [i < num-act]
    [
      if item i chain-weekday = "work" [print (word "PID = " PID " Wrong chain-weekday: " chain-weekday)]
      set i i + 1
    ]
  ]
  print "Check finished"

  ask people with [length plan-weekday != 0 and length chain-weekday = 0 and color != black]
  [
    print (word "PID = " PID " no plan-weekday")
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
623
11
1014
403
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
165
356
280
401
Number of firms
count firms
17
1
11

MONITOR
1026
30
1150
75
Number of people
count people
17
1
11

MONITOR
637
27
694
72
Year
Year
17
1
11

MONITOR
150
568
293
613
Number of Businessmen
count Businessmen
17
1
11

MONITOR
1157
28
1288
73
Number of couples
count spouses
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
1299
27
1429
72
Number of Unemployed people
Count people with [status = 3]
17
1
11

MONITOR
1438
26
1582
71
Number of employees
count people with [status = 2]
17
1
11

MONITOR
1587
25
1725
70
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
631
419
1697
445
-------------------------------------------------------------Residential Location Choice & Real Estate Price Model--------------------------------------------------------
12
0.0
1

TEXTBOX
100
548
605
574
---------------------Businessman Dynamics Model---------------------
12
0.0
1

TEXTBOX
78
334
451
352
---------------------Firm Dynamics Model----------------------
12
0.0
1

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
1024
95
1327
234
Gender
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
696
444
820
489
RF rental volume
res-rent-transaction
17
1
11

MONITOR
833
443
950
488
RF sales volume
res-purchase-transaction
17
1
11

MONITOR
963
442
1087
487
RF average price
ave-rf-price
17
1
11

MONITOR
1098
441
1220
486
RF average rent
ave-RF-rent
17
1
11

MONITOR
631
651
762
696
CFF rental volume
CFF-rent-transaction
17
1
11

MONITOR
770
651
894
696
CFF avearga rent
ave-cff-rent
17
1
11

MONITOR
1166
651
1297
696
CFB rental volume
CFB-rent-transaction
17
1
11

MONITOR
1303
648
1419
693
CFB average rent
ave-CFB-rent
17
1
11

TEXTBOX
1114
10
1625
28
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
301
356
439
401
Employees of firms
sum [size-firm] of firms
17
1
11

MONITOR
300
567
455
612
Employees of businessmen
sum [count in-employee-neighbors] of businessmen
17
1
11

MONITOR
66
624
293
669
Average customer flow (leisure)
ave-leisure-flow
17
1
11

MONITOR
302
624
536
669
Average customer flow (shopping)
ave-shopping-flow
17
1
11

MONITOR
1235
442
1386
487
RF capacity
sum [capacity] of rfs
17
1
11

MONITOR
901
650
1024
695
CFF capacity
sum [capacity] of cffs
17
1
11

MONITOR
1033
651
1158
696
CFF available space
sum [available-space] of CFFs
17
1
11

MONITOR
1426
648
1522
693
CFB capacity
sum [capacity] of CFBs
17
1
11

MONITOR
1530
648
1656
693
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

INPUTBOX
425
15
520
75
Study-Area
Beijing
1
0
String

PLOT
1348
94
1664
234
Status
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Students" 1.0 0 -16777216 true "" "plot count people with [status = 1]"
"Employees" 1.0 0 -7500403 true "" "plot count people with [status = 2]"
"Unemployed people" 1.0 0 -2674135 true "" "plot count people with [status = 3]"
"Retired people" 1.0 0 -955883 true "" "plot count people with [status = 4]"

PLOT
1025
251
1330
402
Age
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"0 - 17" 1.0 0 -16777216 true "" "plot count people with [age < 18]"
"18 - 34" 1.0 0 -7500403 true "" "plot count people with [age >= 18 and age <= 34]"
"35 - 54" 1.0 0 -2674135 true "" "plot count people with [age >= 35 and age <= 54]"
"55 - 74" 1.0 0 -955883 true "" "plot count people with [age >= 55 and age <= 74]"
"> 74" 1.0 0 -6459832 true "" "plot count people with [age > 74]"

PLOT
1349
255
1664
403
People and households
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"People" 1.0 0 -16777216 true "" "plot count people"
"Households" 1.0 0 -7500403 true "" "plot count households"

PLOT
19
165
302
323
Students and employees in school
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Students" 1.0 0 -16777216 true "" "plot sum [count in-student-neighbors] of schools"
"Employees" 1.0 0 -7500403 true "" "plot sum [count in-employee-neighbors] of schools"

PLOT
311
165
616
323
school capacity
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Capacity" 1.0 0 -16777216 true "" "plot sum [capacity] of schools"
"Available space" 1.0 0 -7500403 true "" "plot sum [spa-sch] of schools"

PLOT
18
407
611
546
Distribution of firms
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Firms" 1.0 0 -16777216 true "" "plot count firms"
"Size of firms" 1.0 0 -7500403 true "" "plot sum [count in-employee-neighbors] of firms"

PLOT
14
677
294
827
Number of businessmen
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Shopping" 1.0 0 -16777216 true "" "plot count businessmen with [category = 1]"
"Leisure" 1.0 0 -7500403 true "" "plot count businessmen with [category = 2]"
"Employee-shopping" 1.0 0 -2674135 true "" "plot sum [count in-employee-neighbors] of businessmen with [category = 1]"
"Employee-leisure" 1.0 0 -955883 true "" "plot sum [count in-employee-neighbors] of businessmen with [category = 2]"

PLOT
303
680
606
830
Customer flow
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Flow-shopping" 1.0 0 -16777216 true "" "plot mean [flow] of businessmen with [category = 1]"
"Flow-leisure" 1.0 0 -7500403 true "" "plot mean [flow] of businessmen with [category = 2]"

MONITOR
1397
442
1535
487
RF available space
sum [available-space] of rfs
17
1
11

PLOT
651
501
946
621
Sale volume
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Rental" 1.0 0 -16777216 true "" "plot res-rent-transaction"
"Sale" 1.0 0 -7500403 true "" "plot res-purchase-transaction"

PLOT
958
502
1262
622
Real estate price
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Price" 1.0 0 -16777216 true "" "plot ave-rf-price"
"Rent" 1.0 0 -7500403 true "" "plot ave-rf-rent"

PLOT
1276
501
1611
621
Capacity & Space of RFs
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Capacity" 1.0 0 -16777216 true "" "plot sum [capacity] of RFs"
"Available space" 1.0 0 -7500403 true "" "plot sum [available-space] of RFs"

TEXTBOX
626
631
1680
657
---------------------------------------------------------Firm/Businessman Location Choice & Commercial Faiclity Rent Model----------------------------------------------------
12
0.0
1

PLOT
631
709
894
829
Rental volume
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"CFF" 1.0 0 -16777216 true "" "plot CFF-rent-transaction"
"CFB" 1.0 0 -7500403 true "" "plot CFB-rent-transaction"

PLOT
902
706
1158
829
Rent
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"CFF" 1.0 0 -16777216 true "" "plot ave-cff-rent"
"CFB" 1.0 0 -7500403 true "" "plot ave-cfb-rent"

PLOT
1168
705
1420
829
Capacity and space of CFF
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Capacity" 1.0 0 -16777216 true "" "plot sum [capacity] of CFFs"
"Space" 1.0 0 -7500403 true "" "plot sum [available-space] of CFFs"

PLOT
1427
708
1720
828
Capacity and space of CFB
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Capacity" 1.0 0 -16777216 true "" "plot sum [capacity] of CFBs"
"Available space" 1.0 0 -7500403 true "" "plot sum [available-space] of CFBs"

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
