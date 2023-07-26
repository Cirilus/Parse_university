# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ParserPipeline:

    def set_the_info(self, spider, item):
        try:
            with open(f"{spider}.json", "r") as file:
                data = json.load(file)
        except json.decoder.JSONDecodeError as e:
            with open(f"{spider}.json", "w") as file:
                json.dump(item, file, indent=4, ensure_ascii=False)
            return item
        university = list(item.keys())[0]
        if university not in data:
            data[university] = item[university]
        else:
            data[university] += item[university]
        print(f"data = {data}, spider = {spider}")
        with open(f"{spider}.json", "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return item

    def process_item(self, item, spider):
        print(item)
        self.set_the_info(spider.name, item)

