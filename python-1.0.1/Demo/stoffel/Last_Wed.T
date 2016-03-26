% -- Program: Last_Wed.T
% -- Language: Turing
% -- Written: JCE, 89-3-20
% -- Purpose: To determine the last Wednesday of every month in a given year.

type Days : enum (Su, Mo, Tu, We, Th, Fr, Sa, Invalid)

const Special_day := Days.We /* parameter? */
const Day_name : array Days of string := init
    ("Sun", "Mon", "Tues", "Wednes", "Thurs", "Fri", "Sat", "XXX")

const Jan := 1;  const Feb := 2;  const Dec := 12 /* enum/for problem? */
var Days_in : array Jan .. Dec of 28 .. 31 := init
    (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

fcn Is_leap (Year : int) : boolean
    result Year mod 4 = 0
end Is_leap

fcn Next (Day : Days) : Days
    if Day = Days.Sa then
	result Days.Su
    else
	result succ (Day)
    end if
end Next

proc Get_parameters (var Year : int, var Day_of_week : Days)
    put "Please enter the year, e.g. 89: " ..;
    get Year
    loop
	put "Enter the day of the week that 1 Jan. fell on, e.g. Su: " ..
	var In_day_name : string
	get In_day_name
	for D : Days
	    Day_of_week := D
	    exit when In_day_name (1 .. 2) = Day_name (D) (1 .. 2)
	end for
	exit when Day_of_week not= Days.Invalid
    end loop
end Get_parameters

% -- -- -- -- -- -- -- Main -- -- -- -- -- -- --

var Year : int
var Day_of_week : Days
Get_parameters (Year, Day_of_week)
if Is_leap (Year) then
    Days_in (Feb) := 29
end if

put skip, "Last ", Day_name (Special_day), "day of every month: "

for Month : Jan .. Dec
    for Day_of_month : 1 .. Days_in (Month)
	if Day_of_week = Special_day then
	    if Days_in (Month) - Day_of_month < 7 then
		put Month : 2, ".  ", Year, "-", Month, "-",
		    Day_of_month
	    end if
	end if
	Day_of_week := Next (Day_of_week)
    end for
end for
