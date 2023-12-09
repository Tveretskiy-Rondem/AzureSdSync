import datetime
import time

queryDelayMs = 270

startTime = datetime.datetime.now()
for i in range(100):
    lastTime = datetime.datetime.now()
    if (datetime.datetime.now() - lastTime).microseconds < queryDelayMs:
        time.sleep((queryDelayMs - (datetime.datetime.now() - lastTime).microseconds) / 1000)
        elapsedTime = datetime.datetime.now() - lastTime

print((datetime.datetime.now() - startTime).seconds)
