import csv
import datetime
import numpy as np

def julianDay(gregorianDateTime, calendarOffset = 0):
	"""Conversion of gregorian calendar to julian calendar,
	since julian gives a much more accurate stepping stone
	to calculate solar incidence."""
	year = gregorianDateTime.year
	leapYearTerm = int(year/100)
	month = gregorianDateTime.month
	partialDay = gregorianDateTime.hour*3600.0
	partialDay += gregorianDateTime.minute*60.0
	partialDay += float(gregorianDateTime.second)
	partialDay /= 24.0*60*60
	day = gregorianDateTime.day + partialDay
	calendarOffset = calendarOffset
	firstTerm = lambda year: int(365.25*(year+4716))
	secondTerm = lambda month: int(30.6001*(month+1))
	return firstTerm(year)+secondTerm(month)+day+calendarOffset-1524.5

def julianEphemerisConversion(julianDay, timeDelta):
	"""timeDelta is the difference between earth's rotation time
	and terrestrial time. It's very small, so ephemeris time
	is very nearly identical."""
	return julianDay + (timeDelta/86400.0)

def julianCentury(julianDay):
	return (julianDay-2451545.0)/36525.0

def julianMillennium(julianDay):
	return julianCentury(julianDay)/10.0

def lagrangeContribution(lagrangeMatrix, julianDay):
	JME = julianMillennium(julianDay)
	lagrangeVector = np.zeros(len(lagrangeMatrix))
	for i in range(0,len(lagrangeMatrix)):
		lagrangeVector[i]

def lagrangeTerm(julianDay, filePath):
	"""Returns summed lagrange term"""
	JME = julianMillennium(julianDay)
	lagrange = 0
	with open(filePath, 'rb') as lagrangeData:
		reader = csv.reader(lagrangeData, delimiter=",")
		for row in reader:
			angle = float(row[1])+float(row[2])*JME
			lagrange += float(row[0]) * np.cos(angle)
	return lagrange

def celestialLongitude(gregorianDateTime, lagrangeFiles, gregorian=True, geocentric=False):
	"""Expects lagrangeFiles to be ordered filepaths from 0
	to 5. Also, this can directly take in a gregorian datetime
	object and return the heliocentric Longitude of the earth
	in radians if gregorian is set to false, you can directly
	pass in a julian day, though this is mostly for debugging,
	will return geocentric results if it is set to true, despite the name"""
	if gregorian:
		JDay = julianDay(gregorianDateTime)
	else:
		JDay = gregorianDateTime
	JME = julianMillennium(JDay)
	lagrangeTerms = []
	for filePath in lagrangeFiles:
		lagrangeTerms.append(lagrangeTerm(JDay,filePath))
	longitude = 0
	for i in range(0,len(lagrangeFiles)):
		longitude += lagrangeTerms[i]*(JME**i)
	longitude /= (10.0**8)
	normalizedLongitude = np.arccos(np.cos(longitude))
	if (geocentric):
		return normalizedLongitude + np.pi
	else:
		return normalizedLongitude

def celestialLatitude(gregorianDateTime, latitudeFiles, gregorian=True, geocentric=False):
	"""Basically the same process for a few different things,
	just breaking them up to make the function calls more
	comprehensible"""
	latitude = celestialLongitude(gregorianDateTime, latitudeFiles, gregorian)
	if (geocentric):
		return -latitude
	else:
		return latitude

def radiusVector(gregorianDateTime, radiusFiles, gregorian=True):
	"""See latitude comment"""
	return celestialLongitude(gregorianDateTime, radiusFiles, gregorian)

def meanMoonElongation(gregorianDateTime, gregorian=True):
	"""mean elongation of the moon, again, if gregorian is false
	you can pass in a julian day"""
	if (gregorian):
		JCE = julianCentury(julianDay(gregorianDateTime))
	else:
		JCE = julianCentury(gregorianDateTime)
	firstTerm = lambda century: 297.85036 + 445267.111480*century
	secondTerm = lambda century: 0.0019142*century**2
	thirdTerm = lambda century: (century**3)/189474.0
	degreeAnswer = firstTerm(JCE)-secondTerm(JCE)+thirdTerm(JCE)
	return (degreeAnswer*np.pi)/180.

def meanSunAnomaly(gregorianDateTime, gregorian=True):
	if (gregorian):
		JCE = julianCentury(julianDay(gregorianDateTime))
	else:
		JCE = julianCentury(gregorianDateTime)
	firstTerm = lambda century: 357.52772+35999.050340*century
	secondTerm = lambda century: 0.000163*century**2
	thirdTerm = lambda century: (century**3)/300000.0
	degreeAnswer = firstTerm(JCE)-secondTerm(JCE)-thirdTerm(JCE)
	return (degreeAnswer*np.pi)/180.

def meanMoonAnomaly(gregorianDateTime, gregorian=True):
	if (gregorian):
		JCE = julianCentury(julianDay(gregorianDateTime))
	else:
		JCE = julianCentury(gregorianDateTime)
	firstTerm = lambda century: 134.96298+477198.867398*century
	secondTerm = lambda century: 0.0086972*century**2
	thirdTerm = lambda century: (century**3)/56250.0
	degreeAnswer = firstTerm(JCE)+secondTerm(JCE)+thirdTerm(JCE)
	return (degreeAnswer*np.pi)/180.

def moonLatitudeArgument(gregorianDateTime, gregorian=True):
	if (gregorian):
		JCE = julianCentury(julianDay(gregorianDateTime))
	else:
		JCE = julianCentury(gregorianDateTime)
	firstTerm = lambda century: 93.27191+483202.017538*century
	secondTerm = lambda century: 0.0036825*century**2
	thirdTerm = lambda century: (century**3)/327270.0
	degreeAnswer = firstTerm(JCE)-secondTerm(JCE)+thirdTerm(JCE)
	return (degreeAnswer*np.pi)/180.

def ascendingNodeLongitude(gregorianDateTime, gregorian=True):
	if (gregorian):
		JCE = julianCentury(julianDay(gregorianDateTime))
	else:
		JCE = julianCentury(gregorianDateTime)
	firstTerm = lambda century: 125.04452-1934.136261*century
	secondTerm = lambda century: 0.0020708*century**2
	thirdTerm = lambda century: (century**3)/450000.0
	degreeAnswer = firstTerm(JCE)+secondTerm(JCE)+thirdTerm(JCE)
	return (degreeAnswer*np.pi)/180.

def parseDataToCsv(filePath):
	with open(filePath, 'rb') as rawData:
		counter = 0
		fullMatrix = []
		currentRow = []
		for line in rawData:
			print line
			if counter == 4:
				fullMatrix.append(currentRow)
				counter = counter%4
				currentRow = []
			if "A-" not in line:
				if counter != 0:
					currentRow.append(float(line))
				counter += 1
	with open(filePath, 'wb') as dataDump:
		writer = csv.writer(dataDump, delimiter=",",
							quoting=csv.QUOTE_MINIMAL)
		for row in fullMatrix:
			print row
			writer.writerow(row)

firstLagrange = "data/longitudeFiles/firstLagrangePoint.csv"
secondLagrange = "data/longitudeFiles/secondLagrangePoint.csv"
thirdLagrange = "data/longitudeFiles/thirdLagrangePoint.csv"
fourthLagrange = "data/longitudeFiles/fourthLagrangePoint.csv"
fifthLagrange = "data/longitudeFiles/fifthLagrangePoint.csv"
sixthLagrange = "data/longitudeFiles/sixthLagrangePoint.csv"

firstLatitude = "data/latitudeFiles/firstLatitudePoint.csv"
secondLatitude = "data/latitudeFiles/secondLatitudePoint.csv"

firstRadius = "data/radiusFiles/firstRadius.csv"
secondRadius = "data/radiusFiles/secondRadius.csv"
thirdRadius = "data/radiusFiles/thirdRadius.csv"
fourthRadius = "data/radiusFiles/fourthRadius.csv"
fifthRadius = "data/radiusFiles/fifthRadius.csv"

lagrangeFiles = [firstLagrange,secondLagrange,thirdLagrange, fourthLagrange, fifthLagrange, sixthLagrange]
latitudeFiles = [firstLatitude, secondLatitude]
radiusFiles = [firstRadius, secondRadius, thirdRadius, fourthRadius, fifthRadius]
print(radiusVector(2452930.312847, radiusFiles, False))