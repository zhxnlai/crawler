from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class_Schedule
from pymongo import MongoClient
from scrapy import log


class Class_Schedule_Spider(BaseSpider):
    name = "Class_Schedule"
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

        lecture_numbers = hxs.select('//span[contains(text(), "LEC")][@class="coursehead"]/text()').extract()  
        
        sec_info_link = hxs.select('//td[contains(@class, "IDNumber")]//a/@href').extract()

        IDNumbers = hxs.select('//td[contains(@class, "IDNumber")]//a/@href').re('\d{9}')
        Types = hxs.select('//td[contains(@class, "Type")]//span/text()').extract()
        SectionNumbers = hxs.select('//td[contains(@class, "SectionNumber")]//span/text()').extract()
        Dayss = hxs.select('//td[contains(@class, "Days")]//span/text()').extract()
        TimeStarts = hxs.select('//td[contains(@class, "TimeStart")]//span/text()').extract()
        TimeEnds = hxs.select('//td[contains(@class, "TimeEnd")]//span/text()').extract()
        Buildings = hxs.select('//td[contains(@class, "Building")]//span/text()').extract()
        Rooms = hxs.select('//td[contains(@class, "Room")]//span/text()').extract()
        Restricts = hxs.select('//td[contains(@class, "Restrict")]//span/text()').extract()

        index_of_subject =response.url.find('subareasel=')+len('subareasel=')
        index_of_number= response.url.find('&idxcrs=')+len('&idxcrs=')
        subj = response.url[index_of_subject:index_of_number-len('&idxcrs=')]
        num = response.url[index_of_number:]
        
        subj = subj.replace("+", " ")
        num = num.replace("+", " ")

        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']

        subject_number = list(items.find({'Type':'Class_Brief', 'subject': subj, 'number': num}, {'subject_number':1, '_id':0}))[0]['subject_number']

        #lecturer


        items=[]
        for j in range(len(lecture_numbers)):
            for i in range(len(IDNumbers)):
                item = Class_Schedule()
                item['subject_number'] = subject_number
                item['Type'] = 'Class_Schedule'
                item['lecture_number'] = lecture_numbers[j] if lecture_numbers else None
                item['ID_number'] = IDNumbers[i] if IDNumbers else None

                item['section_type'] = Types[i] if Types else None   
                item['section_number'] = SectionNumbers[i] if SectionNumbers else None
                item['days'] = Dayss[i] if Dayss else None
                item['start'] = TimeStarts[i] if TimeStarts else None
                item['end'] = TimeEnds[i] if TimeEnds else None
                item['building'] = Buildings[i] if Buildings else None
                item['room'] = Rooms[i] if Rooms else None
                item['restrict'] = Restricts[i] if Restricts else None

                item['unique_key'] = IDNumbers[i] if IDNumbers else None


                items.append(item)

        return items