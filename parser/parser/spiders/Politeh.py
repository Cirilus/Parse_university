import json
import os.path

import scrapy
from ..settings import SNILS, NAME


class UniversitySpider(scrapy.Spider):
    name = "Politeh"

    def __init__(self):
        if os.path.exists("Politeh.json"):
            open("Politeh.json", "w").close()
        self.my_snils = SNILS
        self.my_name = NAME

        self.politeh_urls = [
            "https://enroll.spbstu.ru/applications-manager/api/v1/admission-list/form?applicationEducationLevel=BACHELOR&directionEducationFormId=2&directionId=609"

        ]
        self.politeh_direction = [
            "02.03.03 Математическое обеспечение",
        ]

        super().__init__()

    def start_requests(self):
        for url, direction in zip(self.politeh_urls, self.politeh_direction):
            yield scrapy.Request(url, self.parse_Politeh,
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"},
                                 cb_kwargs={"direction": direction}
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
        print(item["заявлений с оригиналом"])
        if "я" in item:
            item["мое место в списке с оригиналами"] = self.my_position(users, item["я"]["баллы"])
        data_direction = [{direction: item}]
        data = {"Политех": data_direction}
        yield data

    def my_position(self, users, my_point):
        sorted_user = sorted(users, key=lambda x: x["баллы"], reverse=True)
        for index, user in enumerate(sorted_user):
            if user["баллы"] <= my_point:
                return index + 1
        return -1
