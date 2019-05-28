result = []
for x in range(1,13):
	result.append((x, (x)))

for x, avg in result:
	print ("This was the average temperature in month number " + str(x) + " in Boston, 2014: ", avg)
