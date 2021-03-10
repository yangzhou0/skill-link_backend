import ssl
from urllib3 import poolmanager
import requests
from requests import adapters
class TLSAdapter(adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        # Heroku is running SECLEVEL 2 causing the problem.
        # We have to lower the strictness because the api.careerstop.org
        # is potentially running on a lower security setting and/or misconfigured.
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)