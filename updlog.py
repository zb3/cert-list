import threading
import sys
import os
from common import *

srv = sys.argv[1] if len(sys.argv) > 1 else 'https://ct.googleapis.com/rocketeer'
srv2 = stripname(srv)

last_id = 0

if len(sys.argv) > 3:
  last_id = int(sys.argv[3])
else:
  try:
    with open('last-id/'+srv2) as f:
      last_id = int(f.read())
  except:
    pass
  
num_threads = int(sys.argv[2]) if len(sys.argv) > 2 else 1
  
print('Last ID: '+str(last_id))

def fetch(url):
  return urllib2.urlopen(url).read()
  
new_last_id = fetch_treesize(srv)
print('New last ID: '+str(new_last_id))

def start_worker(x):
  os.system("python2 get2.py '%s' %d %d %d %d %d >> 'curr/%s-%d'" % (srv, last_id, new_last_id, 1000, x, num_threads, srv2, x))

threads = [threading.Thread(target=start_worker, args=(x,)) for x in xrange(num_threads)]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

with open('last-id/'+srv2, 'w') as f:
  f.write(str(new_last_id))

print('All threads finished.')