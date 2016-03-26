# -- Program: Last_Wed.T
# -- Language: Turing
# -- Written: JCE, 89-3-20
# -- Purpose: To determine the last Wednesday of every month in a given year.

#type Days : enum (Su, Mo, Tu, We, Th, Fr, Sa, Invalid)

l_day = Days.We /* parameter? */# const
me : array Days of string = init# const
    ('Sun', 'Mon', 'Tues', 'Wednes', 'Thurs', 'Fri', 'Sat', 'XXX')

 1;  const Feb = 2;  const Dec := 12 /* enum/for problem? */# const
#var Days_in : array Jan .. Dec of 28 .. 31 = init
    (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

def Is_leap (Year : int) : boolean:  #fcn
    return Year % 4 == 0
#end Is_leap

def Next (Day : Days) : Days:  #fcn
    if Day == Days.Sa:
    return Days.Su
    else:
    return succ (Day)
    #end if
#end Next

def Get_parameters (var Year : int, var Day_of_week : Days):  #proc
    print 'Please enter the year, e.g. 89: ' ..;
    Year = input()
    while 1:
    print 'Enter the day of the week that 1 Jan. fell on, e.g. Su: ',
#    var In_day_name : string
    In_day_name = input()
    for D in range(Day,   for D : Days):
        Day_of_week = D
        if In_day_name (1 .. 2) == Day_name (D) (1 .. 2): break
    #end for
    if Day_of_week not= Days.Invalid: break
    #end loop
#end Get_parameters

# -- -- -- -- -- -- -- Main -- -- -- -- -- -- --

#var Year : int
#var Day_of_week : Days
Get_parameters (Year, Day_of_week)
if Is_leap (Year):
    Days_in (Feb) = 29
#end if

print '\n', 'Last ', Day_name (Special_day), 'day of every month: '

for Month in range(Jan, Dec):
    for Day_of_month in range(1, Days_in (Month)):
    if Day_of_week == Special_day:
        if Days_in (Month) - Day_of_month < 7:
        print Month : 2, '.  ', Year, '-', Month, '-',
            Day_of_month
        #end if
    #end if
    Day_of_week = Next (Day_of_week)
    #end for
#end for
