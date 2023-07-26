import json
import os.path

import scrapy
from ..settings import SNILS, NAME


class UniversitySpider(scrapy.Spider):
    name = "SGTU"

    def __init__(self):
        if os.path.exists("SGTU.json"):
            open("SGTU.json", "w").close()
        self.my_snils = SNILS
        self.my_name = NAME
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

        super().__init__()

    def start_requests(self):
        for url, direction in zip(self.SGTU_urls, self.SGTU_direction):
            yield scrapy.Request(url, self.parse_SGTU,
                                 cb_kwargs={"direction": direction},
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"},
                                 )

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
            dr["я"]["место в списках с оригиналами"] = self.my_position(users, dr["я"]["баллы"])
        # dr[direction] = users
        yield {"СГТУ": [{direction: dr}]}

    def my_position(self, users, my_point):
        sorted_user = sorted(users, key=lambda x: x["баллы"], reverse=True)
        for index, user in enumerate(sorted_user):
            if user["баллы"] <= my_point:
                return index + 1
        return -1
