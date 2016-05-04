try:
  # Python 2 import
  from xmlrpclib import Server
except ImportError:
  # Python 3 import
  from xmlrpc.client import Server

from pprint import pprint

DEV_KEY = 'pSgGvrCuUVArw9wsOt9pRefPP_NjjvIA'

s1 = Server('http://muovi.roma.it/ws/xml/autenticazione/1')
s2 = Server('http://muovi.roma.it/ws/xml/paline/7')

token = s1.autenticazione.Accedi(DEV_KEY, '')

res = s2.paline.Previsioni(token, '70101', 'it')
# pprint(res)
pprint(res['id_richiesta'])
pprint(res['risposta']['arrivi'])