import json
import os.path

import scrapy
from ..settings import SNILS, NAME


class UniversitySpider(scrapy.Spider):
    name = "SBGU"

    def __init__(self):
        if os.path.exists("SBGU.json"):
            open("SBGU.json", "w").close()
        self.my_snils = SNILS
        self.my_name = NAME

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
        for url, direction in zip(self.SBGU_urls, self.SBGU_direction):
            yield scrapy.Request(url, self.parse_SBGU,
                                 cb_kwargs={"direction": direction},
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"},
                                 )

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
            original = info[11].strip()
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
                    "баллы": points,
                })

        item["кол-во людей с оригиналами"] = len(users)
        if "я" in item:
            item["мое место в списке с оригиналами"] = self.my_position(users, item["я"]["баллы"])

        yield {"СБПГЭУ": [{direction: item}]}

    def my_position(self, users, my_point):
        sorted_user = sorted(users, key=lambda x: x["баллы"], reverse=True)
        for index, user in enumerate(sorted_user):
            if user["баллы"] <= my_point:
                return index + 1
        return -1
