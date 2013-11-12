from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class_Detailed
from pymongo import MongoClient
from scrapy import log


class Class_Detailed_Spider(BaseSpider):
    name = "Class_Detailed"
    allowed_domains = ["registrar.ucla.edu"]
    start_urls = []

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']
        current_term = list(items.find({'Type': 'Term', 'name': {'$regex': '^(?!Tentative).*$', '$options': 'i'}}, {'abbrev': 1, '_id':0}).limit(1))[0]['abbrev']
        subj_abbrev_list = list(items.find({'Type': 'Subject'}, {'abbrev': 1, '_id':0}))

        urls = []
        for abbrev in subj_abbrev_list:
            class_number_list=list(items.find({'Type':'Class_Brief', 'subject':abbrev['abbrev']}, {'number': 1, '_id':0}))
            for class_number in class_number_list:
                url = "http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel={0}&subareasel={1}&idxcrs={2}".format(current_term, abbrev['abbrev'].replace(" ","+"), class_number['number'].replace(" ", "+"))

                urls.append(url)

        self.start_urls=urls


    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        item = Class_Detailed()

        item['Type'] = 'Class_Detailed'

        index_of_subject =response.url.find('subareasel=')+len('subareasel=')
        index_of_number= response.url.find('&idxcrs=')+len('&idxcrs=')
        subj = response.url[index_of_subject:index_of_number-len('&idxcrs=')]
        num = response.url[index_of_number:]
        
        subj = subj.replace("+", " ")
        num = num.replace("+", " ")

        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']

        item['subject_number'] = list(items.find({'Type':'Class_Brief', 'subject': subj, 'number': num}, {'subject_number':1, '_id':0}))[0]['subject_number']

        item['name_short_des'] = hxs.select('//tr[@class="SAHeaderDarkGreenBar"]/td/span[contains(@id, "CourseHead")][@class="coursehead"]/text()').extract()

        item['unique_key'] = item['subject_number']+' '+item['Type']
        
        webpage = hxs.select('//a[contains(text(), "Course Webpage")]/@href').extract()
        lib_reserves = hxs.select('//a[contains(text(), "Library Reserves")]/@href').extract()
        textbooks = hxs.select('//a[contains(text(), "Textbooks")]/@href').extract()
        final_exam = hxs.select('//a[contains(text(), "Final Examination")]/@href').extract()

        crs_info = hxs.select('//a[contains(text(), "Crs Info")]/@href').extract()
        ID_number = hxs.select('//a[contains(text(), "Crs Info")]/@href').re('\d{9}')

        if webpage:
            item['webpage'] = webpage[0]
        if lib_reserves:
            item['lib_reserves'] = lib_reserves[0]
        if textbooks:
            item['textbooks'] = textbooks[0]
        if final_exam:
            item['final_exam'] = final_exam[0]
        if ID_number:
            item['ID_number'] = ID_number[0]
        if crs_info:
            item['crs_info'] = crs_info[0]
            url_split = response.url.split("/")
            url_split[-1]=item['crs_info']
            item['crs_info'] = "/".join(url_split)
        else:
            IDNumbers = hxs.select('//td[contains(@class, "IDNumber")]//a/@href').extract()
            if IDNumbers:
                item['crs_info'] = IDNumbers[0]
                url_split = response.url.split("/")
                url_split[-1]=item['crs_info']
                item['crs_info'] = "/".join(url_split)

        items=[]
        items.append(item)
        return items
