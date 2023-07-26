import json
import os.path

import scrapy


class UniversitySpider(scrapy.Spider):
    name = "university"

    def __init__(self):
        if os.path.exists("result.json"):
            open("result.json", "w").close()
        self.my_snils = "168-571-473 09"
        self.my_name = "Попов Станислав Владимирович"
        self.politeh_urls = [
            "https://enroll.spbstu.ru/applications-manager/api/v1/admission-list/form-rating?applicationEducationLevel=BACHELOR&directionEducationFormId=2&directionId=609",

        ]
        self.politeh_direction = [
            "02.03.03 Математическое обеспечение"
        ]

        self.SGTU_urls = [
            "https://abitur.sstu.ru/vpo/direction/2023/11/b/o/b",
            "https://abitur.sstu.ru/vpo/direction/2023/20/b/o/b",
            "https://abitur.sstu.ru/vpo/direction/2023/174/b/o/b"
        ]
        self.SGTU_direction = [
            "Прикладная математика и информатика",
            "Информационные системы и технологии",
            "Программная инженерия"
        ]

        self.SBGU_urls = [
            "https://priem.unecon.ru/stat/stat_konkurs.php?y=2023&filial_kod=1&zayav_type_kod=1&obr_konkurs_kod=0&recomend_type=null&rec_status_kod=all&ob_forma_kod=1&ob_osnova_kod=1&konkurs_grp_kod=4398&prior=all&status_kod=all&is_orig_doc=all&dogovor=all&show=%D0%9F%D0%BE%D0%BA%D0%B0%D0%B7%D0%B0%D1%82%D1%8C",
            "https://priem.unecon.ru/stat/stat_konkurs.php?y=2023&filial_kod=1&zayav_type_kod=1&obr_konkurs_kod=0&recomend_type=null&rec_status_kod=all&ob_forma_kod=1&ob_osnova_kod=1&konkurs_grp_kod=4451&prior=all&status_kod=all&is_orig_doc=all&dogovor=all&show=%D0%9F%D0%BE%D0%BA%D0%B0%D0%B7%D0%B0%D1%82%D1%8C",
            "https://priem.unecon.ru/stat/stat_konkurs.php?y=2023&filial_kod=1&zayav_type_kod=1&obr_konkurs_kod=0&recomend_type=null&rec_status_kod=all&ob_forma_kod=1&ob_osnova_kod=1&konkurs_grp_kod=4446&prior=all&status_kod=all&is_orig_doc=all&dogovor=all&show=%D0%9F%D0%BE%D0%BA%D0%B0%D0%B7%D0%B0%D1%82%D1%8C"

        ]
        self.SBGU_direction = [
            "Прикладная информатика",
            "Прикладная математика и информатика",
            "Информационные системы и технологии"

        ]

        super().__init__()

    def start_requests(self):
        for url, direction in zip(self.politeh_urls, self.politeh_direction):
            yield scrapy.Request(url, self.parse_Politeh,
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"},
                                 cb_kwargs={"direction": direction}
                                 )

        for url, direction in zip(self.SGTU_urls, self.SGTU_direction):
            yield scrapy.Request(url, self.parse_SGTU,
                                 cb_kwargs={"direction": direction},
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"},
                                 )

        for url, direction in zip(self.SBGU_urls, self.SBGU_direction):
            yield scrapy.Request(url, self.parse_SBGU,
                                 cb_kwargs={"direction": direction},
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"},
                                 )


    def parse_Politeh(self, response, **kwargs):
        response = json.loads(response.text)
        users = []
        direction = kwargs.get("direction")
        item = {"кол-во бюджетных мест": response["directionCapacity"],
                "всего поданных заявлений": response["total"],
                "заявлений с оригиналом": response["totalWithOriginals"]}
        for index, user in enumerate(response["list"]):
            if user["userSnils"] == self.my_snils:
                item["я"] = {
                    "снилс": user["userSnils"],
                    "место": int(index),
                    "баллы": int(user["fullScore"]),
                    "приоритет": user["priority"]
                }
                continue
            if user["hasOriginalDocuments"]:
                users.append(
                    {"снилс": user["userSnils"],
                     "место": int(index),
                     "баллы": int(user["fullScore"]),
                     "приоритет": user["priority"], }
                )

        # item["те кто подал оригиналы"] = users
        if "я" in item:
            item["мое место в списке с оригиналами"] = self.my_position(users, item["я"]["баллы"])
        data_direction = [{direction: item}]
        data = {"Политех": data_direction}
        yield data

    def parse_KBGTU(self, response):
        pass

    def parse_SGTU(self, response, **kwargs):
        blocks = response.css(".rasp-block")
        general_list = blocks[-1]
        users = []
        direction = kwargs.get("direction")
        user_blocks = general_list.css("tr")
        dr = {}
        for index, user_block in enumerate(user_blocks):
            if index == 0:
                continue
            info = user_block.css("td::text").extract()
            place = info[0].strip()
            name = info[1].strip()
            points = info[3].strip()
            if points == "—":
                continue
            original = info[-2].strip()
            if name == self.my_name:
                dr["я"] = {
                    "место в общих списках": int(place),
                    "имя": name,
                    "баллы": int(points),
                }
                continue
            if original == "✓":
                users.append({
                    "место": int(place),
                    "имя": name,
                    "баллы": int(points),
                })
        dr["кол-во людей с оригиналами"] = len(users)
        if "я" in dr:
            dr["я"]["место в списках с оригиналами"] = self.my_position(users, 233)
        # dr[direction] = users
        yield {"СГТУ": [{direction: dr}]}

    def parse_SBGU(self, response, **kwargs):
        users = []
        item = {}
        direction = kwargs.get("direction")

        tables = response.css("table")
        general_table = tables[-1]
        user_blocks = general_table.css("tr")
        for index, user_block in enumerate(user_blocks):
            if index == 0:
                continue
            info = user_block.css("td::text").extract()
            snils = user_block.css("td").css("a::text").extract()[0].strip()
            place = info[0].strip()
            points = info[3].strip()
            original = info[-2].strip()
            if snils == self.my_snils:
                item["я"] = {
                    "место": place,
                    "снилс": snils,
                    "баллы": points,
                }
                continue
            if original != "Копия":
                users.append({
                    "место": place,
                    "снилс": snils,
                    "баллы":points,
                })

        item["кол-во людей с оригиналами"] = len(users)
        if "я" in item:
            item["мое место в списке с оригиналами"] = self.my_position(users, item["я"]["баллы"])

        yield {"СБПГЭУ": [{direction: item}]}

    def my_position(self, users, my_point):
        sorted_user = sorted(users, key=lambda x: x["баллы"], reverse=True)
        for user in sorted_user:
            if user["баллы"] <= my_point:
                print(user)
                return user["место"]
        return -1
