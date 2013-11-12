from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class_Schedule
from pymongo import MongoClient
from scrapy import log
import re

class Class_Schedule_Second_Spider(BaseSpider):
    name = "Class_Schedule_Second"
    allowed_domains = ["registrar.ucla.edu"]
    start_urls = []

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']

        current_term = list(items.find({'Type': 'Term', 'name': {'$regex': '^(?!Tentative).*$', '$options': 'i'}}, {'abbrev': 1, '_id':0}).limit(1))[0]['abbrev']
        ID_number=list(items.find({'Type': 'Class_Schedule'},{'ID_number': 1, '_id':0}))

        urls = []
        for ID in ID_number:
            if 'ID_number' in ID:
                url = "http://www.registrar.ucla.edu/schedule/subdet.aspx?srs={0}&term={1}&session=".format(ID['ID_number'], current_term)
                urls.append(url)

        self.start_urls=urls


    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']

        m = re.search('\d{9}', response.url)
        unique_key = m.group(0)

        instructor = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblInstructor"]/text()').extract()
        
        instructor = instructor[0] if instructor else None

        items.update({'unique_key': unique_key},{'$set':{
            'instructor': instructor
            } })