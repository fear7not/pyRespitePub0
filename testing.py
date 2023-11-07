import time
global error
# go test

class reset(Exception):
  def __init__(self, code='none'):
    self.code = code
    print('reset exception raised, code: ' + self.code)


def go(code):
  time.sleep(.2)
  if code == 3:
    print('reset flag raised')
    error = reset(code='timeout')
    raise error
  else: 
    print('reset flag down')

def restart():
  import sys
  print("argv was", sys.argv)
  print("sys.executable was", sys.executable)
  print("restart now")
  import os
  os.execv(sys.executable, ['python'] + sys.argv)

print('test')
restart()
