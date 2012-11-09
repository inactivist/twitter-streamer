import pstats
SORT = 'cumulative'
#SORT = 'time'
LIMIT = 50
p = pstats.Stats('profile2.dat')
p.sort_stats(SORT).print_stats(LIMIT) #.print_callees(LIMIT)


