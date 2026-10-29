"""Temporary localhost CONNECT tunnel. No TLS decryption, credentials or body logging."""
import socket,socketserver,select,threading,json
ALLOWED=('moviein.ajfysu.com',443)
class Tunnel(socketserver.BaseRequestHandler):
 def handle(self):
  upstream=None
  try:
   header=b''
   while b'\r\n\r\n' not in header and len(header)<8192:
    part=self.request.recv(1024)
    if not part:return
    header+=part
    if header.startswith(b'STOP\n'):
     self.request.sendall(b'OK\n');threading.Thread(target=self.server.shutdown,daemon=True).start();return
   line=header.split(b'\r\n',1)[0].decode('ascii','replace')
   parts=line.split()
   if len(parts)!=3 or parts[0]!='CONNECT' or parts[1]!=f'{ALLOWED[0]}:{ALLOWED[1]}':
    self.request.sendall(b'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n');return
   upstream=socket.create_connection(ALLOWED,timeout=10)
   self.request.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
   remainder=header.split(b'\r\n\r\n',1)[1]
   if remainder:upstream.sendall(remainder)
   print(json.dumps({'event':'tunnel.connected','host':ALLOWED[0],'tls_decryption':False}),flush=True)
   self.request.settimeout(None);upstream.settimeout(None)
   while True:
    readable,_,_=select.select([self.request,upstream],[],[],30)
    if not readable:return
    for source in readable:
     data=source.recv(65536)
     if not data:return
     (upstream if source is self.request else self.request).sendall(data)
  except Exception as e:print(json.dumps({'event':'tunnel.error','type':type(e).__name__}),flush=True)
  finally:
   if upstream:upstream.close()
class Server(socketserver.ThreadingTCPServer):
 allow_reuse_address=True
 daemon_threads=True
with Server(('127.0.0.1',18080),Tunnel) as server:
 print('Temporary API-only CONNECT tunnel listening on localhost:18080',flush=True)
 server.serve_forever()
