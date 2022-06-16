from base64 import b64decode
import requests as rq
from pprint import pprint
from os.path import join as pjoin
import os
import sys
import config as cf
import json

KEYb64="cnVqYnZ4NzQ4Nw=="
KEY = b64decode(KEYb64).decode("utf8")
URL = "https://catalog.api.2gis.com/3.0/"

OUTDIR = cf.IMG

# Ошибки, связанные с протоколом 2GIS
class APIException(Exception):
    pass

# Ошибки, связанные с соединением с 2GIS
class APIHTTPException(APIException):
    pass

# Ошибки, связанные с неправильными данными от пользователя
class DGISException(Exception):
    pass

# "items?q=ИГУ&sort_point=37.630866,55.752256&ke"

# Перечень интересующих нас полей об организации
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

# Класс-фасад, представляющий собой API 2GIS
class DGIS:
    def __init__(self, key):
        self.key = key
        self.setupfields(**FIELDS)

    def api(self, method, **kwargs):
        global KEY

        if "key" in kwargs:
            raise DGISException("Keyword 'key' is not allowed")

        kwargs["key"] = self.key
        # pprint(kwargs)
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


# Класс, позволяющий с JSON работать юез исплользования
# лишних скобок и кавычек
class JObject:
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        return JObject(self.obj.get(name))

    def __getitem__(self, index):
        return JObject(self.obj[index])

    def __str__(self):
        return str(self.obj)

    @property
    def s(self):
        return str(self)


# Класс-адаптер структуры JSON, возвращаемой 2GIS в
# структуру генератора LandingPage и другие файлы (картинки)
class DescribeBranch(JObject):

    def header(self):
        return "Header", {
            "title": self.name_ex.legal_name.s,
            "paragraph": self.full_address_name.s}


    def wt(self):
        days = self.schedule
        answer = ["Время работы"]
        for day, wh in days.obj.items():
            s = ""
            for interval in JObject(wh).working_hours:
                f = interval["from"]
                t = interval["to"]
                s+="{} - {} <br/>".format(f, t)
            answer.append("{}<br/>{}".format(day, s))
        return answer

    def about(self):
        return "About", {
            "paragraph": "",
            "Why2": self.wt(),
            "Why": [
                self.name_ex.description.s,
                "Адрес:",
                self.full_address_name.s,
                "",
            ],
        }

    def description(self):
        d = {}
        for m in [self.header, self.about]:
            k, v = m()
            d[k] = v

        return d


    def dl(self, url, fn):
        fn = pjoin(OUTDIR, fn)

        os.system("curl '{}' --output '{}'".format(url, fn))

    def aboutimage(self):

        # import pudb; pu.db

        try:
            url = self.external_content[0]\
                      .main_photo_url.s
        except (AttributeError, IndexError):
            print("Could'nt recognize about image")
            return

        self.dl(url, "about.jpg")


    def convert(self):

        self.aboutimage()
        return self.description()

    def convertandsave(self):
        js = self.convert()
        o = open(pjoin(cf.DATA, "data.json"), "w")
        json.dump(js, o, ensure_ascii=False, indent=4)
        o.close()


    def services(self):
        return "Services", []

# главная проргамма преобразрвания запроса в Landing Page
if __name__=="__main__":
    api = DGIS(KEY)

    # r = api.search(q="ИГУ Иркутск")

    query = " ".join(sys.argv[1:])

    r = api.branch(query)
    res = r["result"]
    items = res["items"]

    print(" Список найденных организаций")
    for i, item in enumerate(items):
        j = DescribeBranch(item)

        h = j.header()[1]["title"]
        print("{} - '{}'".format(i+1, h))
    if not items:
        print("пуст!")
        quit()

    if items:
        choice = input("-> ")
        try:
            choice = int(choice)
        except ValueError:
            print("Надо было ввести число. Выходим.")
            quit()
        if choice<=0:
            print("Вввести надо было натуральное число большее нуля. Выходим.")
            quit()
        if choice>len(items):
            print("Введенное число больше количества вариантовю Выходим")
            quit()

    choice -= 1

    for item in items[choice:choice]:   # Найденные предприятия
        # pprint(item)
        d = DescribeBranch(item)
        # pprint(d.convert())
        d.convertandsave()
