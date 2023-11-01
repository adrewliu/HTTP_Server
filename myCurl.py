import socket
import sys
import re
import csv
import traceback
#from urlparse import urlparse, urlsplit



class Error(Exception):
  """Base class for other exceptions"""
  pass

class PortError(Error):
  """Raised when port number is 443"""
  pass

class HTTPSError(Error):
  """Raised when the HTTPS protocol is used"""
  pass

class ConnectionsError(Error):
  """Raised when connection failed"""
  pass

header = []


def create_sock():
  global remote_ip
  global hostname
  global port
  global s

  try:
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  except socket.error as msg:
    print("Socket creation error: " + str(msg))
  try:
    hostname = socket.gethostname()
    remote_ip = socket.gethostbyname(hostname)
  except socket.gaierror:
    print('Hostname could not be resolved. Exiting')
    sys.exit()

def is_ip(s):
  if(s is not None):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True
  else:
    print("not an IP")

def socket_regex(address):
  global port
  global server_name 
  server_name = ""
 
  ip_reg = re.compile('^(?P<proto>[^:\/?#]+):\/\/(?P<ip>[^@\/?#:]*)?:?(?P<port>\d+)?\/?(?P<path>[\w.?\w?]*)? ?')
  url_re = re.search(ip_reg, address)
  try:
    proto = url_re.group(1).strip('[').strip('\'')
  except AttributeError:
    proto = re.match('(\w+):\/\/', address)
  try:
    www = re.findall(' ?(www.[\w\-\.]+)?', address)
    for i in www:
      if i != "":
        server_name = i
    org = re.findall('\w+.org', address)
    for i in org:
      if i != "":
        server_name = i
  except AttributeError:
    print(server_name)

  try:
    port = url_re.group(3)
    if port == None:
      port = 80
    else:
      port = int(port)
    #port = re.match(':(\d*)?', address).group(3)
  except AttributeError:
    port = re.match(':(\d*)?', address)
  
  try:
    path = url_re.group(4).strip(',').strip('\\')
  except AttributeError:
    path = re.match('.*\/([^#?]*) ', address)

  print("protocol: ", proto)
  print("host: ", server_name)
  print("port: ", port)
  print("path: ", path)
 
  making_connections(proto, server_name, port, path)

def making_connections(protocol, server_name, server_port, path):
  global host_ip

  try:
    host_ip = socket.gethostbyname(server_name)
    
  except socket.gaierror:
    print ("there was an error resolving the host")
    sys.exit()
  conn = False
  while conn == False:
    try:
      s.connect((host_ip, server_port))
      conn = True
      if (is_ip(server_name)):
        server_name = s.gethostbyaddr(server_name)

      if server_port == 443:
        raise PortError
      elif protocol == "HTTPS":
        raise HTTPSError
      break
    except PortError:
      print("Port cannot be used")
      print()
    except HTTPSError:
      print("HTTPS protocol cannot be used")
      print()
    except ConnectionsError:
      print("Error accepting connections")
      print()
    except socket.error as msg:
      print("Socket creation error: " + str(msg)) 
      break

  send_request(server_name, path)

def send_request(address, path):

  request_header = 'GET /' + path +  ' HTTP/1.1\r\nHost: ' + address + '\r\n\r\n' 
  #print(s.send(request_header))
  #s.sendall(request_header.encode()
  #s.sendall(b"GET / HTTP/1.1\r\nHost: www.cnn.com\r\n\r\n")
  #s.sendall('GET /' + path +  ' HTTP/1.1\r\nHost: ' + address + '\r\n\r\n'.encode('ascii'))
  while True:
    try:
      s.sendall(request_header.encode('utf-8'))
      receive_response()
    
    except socket.error as msg:
      print(address, str(msg))
      print("request failed")
      s.close()
      sys.exit()
  
  '''read lines from html file and retrieve the csv field values'''
# def log_csv(retrieval, statuscode, response):
#   print(retrieval)
#   print(statuscode)
#   with open('log.csv', 'w') as csvfile:
#     fieldnames = ['Retrieval', 'Status Code', 'URL', 'Hostname', 'Src IP', 'Dst IP', 'Server Response']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()
#     #rows = [{'Retrieval': retrieval, 'Status Code':statuscode , 'URL':server_name, 'Hostname':remote_ip, 'Scr IP': host_ip, 'Dst IP': remote_ip), 'Server Response': response}]
      
#     # for i in header:
#     #   writer.writerows(rows)

def receive_response():
  # retrieval = False
  # statuscode = 'OK 200'
  file = open('HTTPoutput.html', 'w')
  success = True
  data = b''
  while success:
    try:
      d = s.recv(2048).decode('utf-8')
      print(data)
      header.append(data)
      file.write(data)
      #log_csv(retrieval, statuscode, server_name, hostname, )
      if not d:
        success = False
        print("no more data to receive")
        s.close()
        sys.exit()
      data += d
      
    except socket.error:
      # retrieval = False
      # statuscode = 'Not Found'
      #log_csv(retrieval, statuscode, data.decode('utf-8'))
      print("Unsuccessful Retreival", server_name)
      s.close()
      sys.exit()

      # if data is  None:
      #   success = False
      #   print("no more data to receive")
      #   s.close()
      #   sys.exit()

    # writer.writerow({'Retrieval': 'Success', 'Status Code': 'True', 'URL':address, 'Hostname':s.gethostbyname(address), 'Scr IP': address, 'Dst IP': s.gethostbyname(address), 'Server Response': request_header}
    # if data is None:
    #   raise RequestError
    #   writer.writerow({'Retrieval': 'Unsuccess', 'Status Code': 'False', 'URL':address, 'Hostname':s.gethostbyname(address), 'Scr IP': address, 'Dst IP': s.gethostbyname(address), 'Server Response': request_header}
    #   print data.decode()
    #   break


if __name__ == '__main__':
  address = str(sys.argv[1:])
  create_sock()
  socket_regex(address)
  s.close()    