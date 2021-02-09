import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
# This is the 2.11 Requests cipher string, containing 3DES.
CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)
class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)
    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super().proxy_manager_for(*args, **kwargs)

url = "https://api.careeronestop.org/v1/occupation/wsDcyeU9muW1AxN/Chemical%20Technicians/11101?training=true&interest=false&videos=true&tasks=false&dwas=true&wages=true&alternateOnetTitles=true&projectedEmployment=true&ooh=false&stateLMILinks=false&relatedOnetTitles=true&skills=true&knowledge=true&ability=true&trainingPrograms=true"

headers = {"Authorization": "Bearer +h3F09pWZZGpREt8CJ15xFwJIgVHTPzMzmki22tnMRPHuVnoYy8W6a2MI3xLfXZPF3nM6DBqoSyc5aRfnThtBg=="}

s = requests.Session()
s.mount('https://', MyAdapter())
response = s.get(url,headers = headers)
print(response)