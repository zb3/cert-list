import urllib2
import json
import base64
from struct import unpack
import OpenSSL.crypto
import time
import re
import sys

def stripname(srv):
  return re.sub(r'[^0-9a-z]', '', srv)

def fetch(url):
  return urllib2.urlopen(url).read()

def unpack_tls_array(packed_data, length_len):
    padded_length = ["\x00"] * 8
    padded_length[-length_len:] = packed_data[:length_len]
    (length,) = unpack(">Q", "".join(padded_length))
    unpacked_data = packed_data[length_len:length_len+length]
    assert len(unpacked_data) == length, \
      "data is only %d bytes long, but length is %d bytes" % \
      (len(unpacked_data), length)
    rest_data = packed_data[length_len+length:]
    return (unpacked_data, rest_data)
  
def unpack_mtl(merkle_tree_leaf):
    version = merkle_tree_leaf[0:1]
    leaf_type = merkle_tree_leaf[1:2]
    timestamped_entry = merkle_tree_leaf[2:]
    (timestamp, entry_type) = unpack(">QH", timestamped_entry[0:10])
    if entry_type == 0:
        issuer_key_hash = None
        (leafcert, rest_entry) = unpack_tls_array(timestamped_entry[10:], 3)
    elif entry_type == 1:
        issuer_key_hash = timestamped_entry[10:42]
        (leafcert, rest_entry) = unpack_tls_array(timestamped_entry[42:], 3)
    return (leafcert, timestamp, issuer_key_hash)

def extract_precertificate(precert_chain_entry):
    (precert, certchain) = unpack_tls_array(precert_chain_entry, 3)
    return (precert, certchain)
    
def decode_certificate_chain(packed_certchain):
    (unpacked_certchain, rest) = unpack_tls_array(packed_certchain, 3)
    assert len(rest) == 0
    certs = []
    while len(unpacked_certchain):
        (cert, rest) = unpack_tls_array(unpacked_certchain, 3)
        certs.append(cert)
        unpacked_certchain = rest
    return certs

def extract_original_entry(entry):
    leaf_input =  base64.decodestring(entry["leaf_input"])
    (leaf_cert, timestamp, issuer_key_hash) = unpack_mtl(leaf_input)
    extra_data = base64.decodestring(entry["extra_data"])
    if issuer_key_hash != None:
        (precert, extra_data) = extract_precertificate(extra_data)
        leaf_cert = precert
    certchain = decode_certificate_chain(extra_data)
    return ([leaf_cert] + certchain, timestamp, issuer_key_hash)
    
def fetch_certs(srv, start, end):
  return json.loads(fetch(srv+'/ct/v1/get-entries?start='+str(start)+'&end='+str(end)))
  
def fetch_treesize(srv):
  return json.loads(fetch(srv+'/ct/v1/get-sth'))['tree_size']
    
    
oids = [    "1.3.6.1.4.1.34697.2.2",
            "1.3.6.1.4.1.34697.2.1", 
            "1.3.6.1.4.1.34697.2.3", 
            "1.3.6.1.4.1.34697.2.4",
            "1.2.40.0.17.1.22",
            "2.16.578.1.26.1.3.3",
            "1.3.6.1.4.1.17326.10.14.2.1.2", 
            "1.3.6.1.4.1.17326.10.14.2.2.2", 
            "1.3.6.1.4.1.17326.10.8.12.1.2",
            "1.3.6.1.4.1.17326.10.8.12.2.2",
            "1.3.6.1.4.1.6449.1.2.1.5.1",
            "2.16.840.1.114412.2.1",
            "2.16.528.1.1001.1.1.1.12.6.1.1.1",
            "2.16.840.1.114028.10.1.2",
            "1.3.6.1.4.1.14370.1.6",
            "1.3.6.1.4.1.4146.1.1",
            "2.16.840.1.114413.1.7.23.3",
            "1.3.6.1.4.1.14777.6.1.1", 
            "1.3.6.1.4.1.14777.6.1.2",
            "1.3.6.1.4.1.22234.2.5.2.3.1",
            "1.3.6.1.4.1.782.1.2.1.8.1",
            "1.3.6.1.4.1.8024.0.2.100.1.2",
            "1.2.392.200091.100.721.1",
            "2.16.840.1.114414.1.7.23.3",
            "1.3.6.1.4.1.23223.2", 
            "1.3.6.1.4.1.23223.1.1.1", 
            "1.3.6.1.5.5.7.1.1",
            "2.16.756.1.89.1.2.1.1",
            "2.16.840.1.113733.1.7.48.1",
            "2.16.840.1.114404.1.1.2.4.1",
            "2.16.840.1.113733.1.7.23.6",
            "1.3.6.1.4.1.6334.1.100.1",
            "1.3.159.1.17.1",
            "1.3.6.1.4.1.13177.10.1.3.10",
            "1.3.6.1.4.1.36305.2",
            "1.2.616.1.113527.2.5.1.1",
            "1.3.6.1.4.1.29836.1.10",
            "1.3.6.1.4.1.4788.2.202.1",
            "2.16.792.3.0.4.1.1.4",
            "2.16.528.1.1003.1.2.7",
            "2.16.840.1.114414.1.7.24.3",
            "2.16.756.1.83.21.0",
            "1.3.6.1.4.1.40869.1.1.22.3",
            "1.3.6.1.4.1.7879.13.24.1",
            "2.16.840.1.114171.500.9",
            "2.16.840.1.114404.1.1.2.4.1"
            ]

def print_cert_info(cert, counter):
  (chain, timestamp, hash) = extract_original_entry(cert)
    
  x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, chain[0])
  
  if not x509.get_subject().commonName:
    return
  
  header = 'ID: '+str(counter)+', '+time.strftime('%Y%m%d%H%M%SZ',time.gmtime(timestamp/1000))+', '+x509.get_notBefore()+' - '+x509.get_notAfter()
  
  for x in xrange(x509.get_extension_count()):
    try:
      xt = x509.get_extension(x)
      if xt.get_short_name() == 'certificatePolicies':
         tostr = str(xt)
         for ln in tostr.split('\n'):
           if ': ' in ln and ln[ln.index(': ')+2:] in oids:
             header += ', EV='+x509.get_subject().organizationName+' ('+x509.get_subject().countryName+')'
             break
    except:
      print
      pass
  
  print(header.encode('utf8'))

  cn = x509.get_subject().commonName.lower()
  print(cn.encode('utf8'))
     
  for x in xrange(x509.get_extension_count()):
    try:
      xt = x509.get_extension(x)
      if xt.get_short_name() == 'subjectAltName':
        sanlist = str(xt).split(', ')
        for entry in sanlist:
          if entry == 'othername:<unsupported>':
            continue
            
          san = entry[entry.index(':')+1:]
            
          if san != cn and san != 'www.'+cn and 'www.'+san != cn:
            print(san.encode('utf8'))
         

    except:
      pass
         
  print('')
