#! venv/bin/python

import unittest
import datetime

import extract

class TestExtract(unittest.TestCase):
	def setUp(self):
		self.expected_tr = {'fore': [{'date': datetime.date(2016, 8, 26), 'day': 'Friday', 'rain': 19, 'temp': 89},
				{'date': datetime.date(2016, 8, 27), 'day': 'Saturday', 'rain': 0, 'temp': 88},
				{'date': datetime.date(2016, 8, 28), 'day': 'Sunday', 'rain': 0, 'temp': 88},
				{'date': datetime.date(2016, 8, 29), 'day': 'Monday', 'rain': 11, 'temp': 92},
				{'date': datetime.date(2016, 8, 30), 'day': 'Tuesday', 'rain': 2, 'temp': 88},
				{'date': datetime.date(2016, 8, 31), 'day': 'Wednesday', 'rain': 2, 'temp': 89},
				{'date': datetime.date(2016, 9, 1), 'day': 'Thursday', 'rain': 0, 'temp': 84},
				{'date': datetime.date(2016, 9, 2), 'day': 'Friday','rain': 20, 'temp': 76}],
		    'noaa': [{'date': datetime.date(2016, 8, 27),'day': 'Saturday','rain': 0,'temp': 88},
		  		{'date': datetime.date(2016, 8, 28),'day': u'Sunday','rain': 70,'temp': 84},
		  		{'date': datetime.date(2016, 8, 29),'day': u'Monday','rain': 0,'temp': 78},
		    	{'date': datetime.date(2016, 8, 30),'day': u'Tuesday','rain': 0,'temp': 78},
		    	{'date': datetime.date(2016, 8, 31),'day': u'Wednesday','rain': 0,'temp': 84},
		        {'date': datetime.date(2016, 9, 1),'day': u'Thursday','rain': 0,'temp': 84},
		        {'date': datetime.date(2016, 9, 2),'day': u'Friday','rain': 40,'temp': 85}],
		    'wu': [{'date': datetime.date(2016, 8, 26),'day': u'Friday','rain': 20,'temp': 91},
		  		{'date': datetime.date(2016, 8, 27),'day': u'Saturday','rain': 0,'temp': 88},
		  		{'date': datetime.date(2016, 8, 28),'day': u'Sunday','rain': 10,'temp': 89},
		  		{'date': datetime.date(2016, 8, 29),'day': u'Monday','rain': 20,'temp': 90},
		  		{'date': datetime.date(2016, 8, 30),'day': u'Tuesday','rain': 10,'temp': 90},
		  		{'date': datetime.date(2016, 8, 31),'day': u'Wednesday','rain': 10,'temp': 91},
		  		{'date': datetime.date(2016, 9, 1),'day': u'Thursday','rain': 10,'temp': 86},
		  		{'date': datetime.date(2016, 9, 2),'day': u'Friday','rain': 10,'temp': 84},
		  		{'date': datetime.date(2016, 9, 3),'day': u'Saturday','rain': 20,'temp': 81}]}
		  		
		
	def testGetData(self):
		data = extract.get_data(offline=True)
		tr = extract.get_temp_rain(data)
		self.assertEqual(tr, expected)


if __name__=='__main__':
	unittest.main()