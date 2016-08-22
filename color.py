################### Number to Color Functions ########################
def scale(num, ostart, oend, nstart, nend):
	""" num is on a scale from (ostart, oend) gets shifted to scale (nstart, nend) """
	
	return ((float(num) - float(ostart)) / (float(oend) - float(ostart))) * (float(nend) - float(nstart)) + float(nstart)

def temp_to_color(temp):
	if temp > 90:
		result = "FF3333"
	elif temp > 77.5:
		result = ("FF%02x33" % scale(temp, 90, 77.5, 0x33, 0xff)).upper()
	elif temp > 65:
		result = ("%02xFF33" % scale(temp, 77.5, 65, 0xff, 0x33)).upper()
	elif temp > 52.5:
		result = ("33FF%02x" % scale(temp, 65, 52.5, 0x33, 0xff)).upper()
	elif temp > 40:
		result = ("33%02xFF" % scale(temp, 52.5, 40, 0xff, 0x33)).upper()
	else:
		result = "3333FF"
	return result

def rain_to_color(rain):
	if rain < 33:
		result = ("33FF%02x" % scale(rain, 0, 33, 0x33, 0xff)).upper()
	elif rain < 66:
		result = ("33%02xFF" % scale(rain, 33, 66, 0xff, 0x33)).upper()
	else:
		result = ("%02x33FF" % scale(rain, 66, 100, 0x33, 0xc3)).upper()
	return result