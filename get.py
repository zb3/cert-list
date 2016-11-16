import sys
from common import *

srv = sys.argv[3] if len(sys.argv) > 3 else 'https://ct.googleapis.com/rocketeer'
srv2 = stripname(srv)

start = int(sys.argv[1])
delta = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
end = start+delta-1

tsize = fetch_treesize(srv)
print('Tree size: '+str(tsize))

counter = start

fetched_certs = fetch_certs(srv, start, end)

for c in fetched_certs['entries']:
  print_cert_info(c, counter)
  counter += 1
    
    