import sys
from common import *

srv = sys.argv[1]
srv2 = stripname(srv)

start = int(sys.argv[2])
end = int(sys.argv[3])
step = int(sys.argv[4])
modulus = int(sys.argv[5])
modall = int(sys.argv[6])

curr = start
print('SYNC', start)

def download_certs(start, end): 
  fetched_certs = fetch_certs(srv, start, end)
  
  counter = start
  for c in fetched_certs['entries']:
    print_cert_info(c, counter)
    counter += 1


while curr<end:
  if (curr // step) % modall == modulus:
    download_certs(curr, min(curr+step, end-1))
  
  curr += step
