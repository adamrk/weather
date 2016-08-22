#! venv/bin/python

from blinkstick import blinkstick
import time

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

bstick = blinkstick.find_first()

for i in range(100):
	for j in range(8):
		bstick.set_color(index=j, name=colors[(i+j) % 7])
		time.sleep(0.05)

for j in range(8):
	bstick.set_color(index=j, name='black')