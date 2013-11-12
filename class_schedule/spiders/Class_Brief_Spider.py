from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class_Brief
from pymongo import MongoClient
from scrapy import log

class Class_Brief_Spider(BaseSpider):
    name = "Class_Brief"
    allowed_domains = ["registrar.ucla.edu"]
    start_urls= []

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']
        current_term = list(items.find({'Type': 'Term', 'name': {'$regex': '^(?!Tentative).*$', '$options': 'i'}}, {'abbrev': 1, '_id':0}).limit(1))[0]['abbrev']
        abbrev_list = list(items.find({'Type': 'Subject'}, {'abbrev': 1, '_id':0}))

        #log.msg('current_term is {}'.format(current_term))

        urls = []
        for abbrev in abbrev_list:
            url = "http://www.registrar.ucla.edu/schedule/crsredir.aspx?termsel={0}&subareasel={1}".format(current_term, abbrev['abbrev'].replace(" ","+"))
            urls.append(url)
        self.start_urls=urls

    def parse(self, response):
        log.msg('crawling url {}'.format(response.url))

        sel = HtmlXPathSelector(response)
        class_names = sel.select('//option/text()').extract()
        class_numbers = sel.select('//option/@value').extract()
              
        items=[]
        for i in range(len(class_names)):
            item = Class_Brief()
            item['Type'] = 'Class_Brief'
            item['name_des'] = class_names[i]
            index_of_hypen = class_names[i].find(' - ')
            item['subject_number'] = class_names[i][0:index_of_hypen]
            item['unique_key'] = item['subject_number']
            item['number'] = class_numbers[i]

            index_of_last_space = item['subject_number'].rfind(' ')
            item['subject'] = item['subject_number'][0:index_of_last_space]
 

            items.append(item)

        return items