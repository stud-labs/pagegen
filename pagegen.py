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

FIELDS = {
    "items.point": "координаты объекта, заданные в системе координат WGS84 в формате lon, lat",
    "items.address": "адрес, по которому располагается объект",
    "items.adm_div": "принадлежность к административной территории",
    "items.full_address_name": "адрес объекта с указанием города",
    "items.geometry.centroid": "визуальный центр геометрии объекта",
    "items.geometry.hover": "геометрия области, используемой для определения попадания курсора в зону объекта",
    "items.geometry.selection": "геометрия для выделения объекта",
    "items.rubrics": "категории компании",
    "items.org": "организация, к которой относится филиал",
    "items.contact_groups": "контакты компании",
    "items.schedule": "расписание работы компании",
    "items.access_comment": "локализованное название для типа доступа",
    "items.access": "тип доступа для парковки",
    "items.capacity": "вместимость парковки",
    "items.description": "описание геообъекта",
    "items.external_content": "дополнительные данные компании, такие как буклеты и фотографии",
    "items.flags": "список признаков объекта",
    "items.floors": "количество этажей",
    "items.floor_plans": "планы этажей",
    "items.is_paid": "является ли парковка платной",
    "items.for_trucks": "парковка для грузовиков",
    "items.paving_type": "тип покрытия парковки",
    "items.is_incentive": "является ли парковка перехватывающей",
    "items.purpose": "назначение парковки",
    "items.level_count": "количество уровней парковки",
    "items.links": "связанные объекты",
    "items.links.database_entrances.apartments_info": "информация о квартирах в доме",
    "items.name_ex": "составные части наименования объекта",
    "items.reviews": "отзывы об объекте",
    "items.statistics": "cводная информация о геообъекте",
    "items.employees_org_count": "численность сотрудников организации",
    "items.itin": "индивидуальный номер налогоплательщика",
    "items.trade_license": "лицензия филиала",
    "items.fias_code": "код ФИАС улиц и административных территорий",
    "items.address.components.fias_code": "код ФИАС зданий",
    "items.attribute_groups": "дополнительные атрибуты компании",
    "items.delivery": "есть доставка",
    "items.has_discount": "есть скидки",
    "items.caption": "название объекта",
    "items.routes": "маршруты транспорта, проходящие через станцию или остановку",
    "items.directions": "направления маршрута",
    "items.entrance_display_name": "показать номер входа на станцию метро, если объект является входом (station_entrance)",
    "items.platforms": "остановочные платформы остановки",
    "items.floor_id": "идентификатор этажа",
}

class DGIS:
    def __init__(self, key):
        self.key = key
        self.setupfields(**FIELDS)

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

    def search(self, q, **kwargs):
        return self.api("items", q=q, **kwargs)

    def branch(self, q, **kwargs):
        kwargs["q"]=q
        kwargs["type"]="branch"

        if self.fields:
            kwargs["fields"]=','.join((k for k in self.fields.keys()))

        return self.api("items", **kwargs)

    def setupfields(self, **kwargs):
        self.fields = kwargs

    def __setitem__(self, field, val):
        self.fields[field] = val




if __name__=="__main__":
    api = DGIS(KEY)

    # r = api.search(q="ИГУ Иркутск")

    r = api.branch("ИГУ Иркутск")

    pprint(r)
