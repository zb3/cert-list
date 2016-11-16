import sys
import os
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('--ev', action='store_true')
parser.add_argument('--valid', action='store_true')
parser.add_argument('--dirname', default='curr')
parser.add_argument('--destdirname', default='filtered')
args = parser.parse_args()

count = 44

def process_file(name):  
  with open(os.path.join(args.destdirname, name), 'w') as outfile:
    with open(os.path.join(args.dirname, name)) as infile:
      state = 0 #0 - fetch ID line, 1 - accept, 2 - reject
      
      for line in infile:
        if state == 0:
          if not line.startswith('ID: '):
            continue
          
          nstate = 1
          lparts = line.split(', ')
          
          if args.valid:
            enddate = lparts[2].split(' - ')[1] if ' - ' in lparts[2] else None
            
            if not enddate or enddate<time.strftime('%Y%m%d%H%M%SZ',time.gmtime(time.time())):
              nstate = 2
          
          if args.ev and not ', EV=' in line:
            nstate = 2
            
          if nstate == 1:
            outfile.write(line)
            
          state = nstate
            
        else:
          if state == 1:
            outfile.write(line)
                              
          if not line or line == '\n':
            state = 0            
            

for fd in os.listdir(args.dirname):
  fn = os.path.join(args.dirname, fd)
  
  if not os.path.isfile(fn):
    continue
    
  process_file(fd)
  
  
