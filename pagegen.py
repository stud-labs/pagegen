from base64 import b64decode
import requests as rq
from pprint import pprint

KEYb64="cnVqYnZ4NzQ4Nw=="
KEY = b64decode(KEYb64).decode("utf8")
URL = "https://catalog.api.2gis.com/3.0/"


class APIException(Exception):
    pass

class APIHTTPException(APIException):
    pass

class DGISException(Exception):
    pass

# "items?q=ИГУ&sort_point=37.630866,55.752256&ke"

class DGIS:
    def __init__(self, key):
        self.key = key

    def api(self, method, **kwargs):
        global KEY

        if "key" in kwargs:
            raise DGISException("Keyword 'key' is not allowed")

        kwargs["key"] = self.key
        pprint(kwargs)
        resp = rq.get(URL+method, params=kwargs)
        if not str(resp.status_code).startswith("20"):
            raise APIHTTPException("API HTTP Error")
        answer =  resp.json()
        meta = answer["meta"]
        if "error" in meta:
            raise APIException(meta["error"]["message"])
        return answer

    def __call__(self, method, **kwargs):
        return self.api(method, **kwargs)

api = DGIS(KEY)

r = api(method="items", what="ИГУ", where="Иркутск")

pprint(r)
