from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class_Enrollment
from pymongo import MongoClient
from scrapy import log


class Enrollment_Number_Spider(BaseSpider):
    name = "Enrollment_Number"
    allowed_domains = ["registrar.ucla.edu"]
    start_urls = []

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']
        current_term = list(items.find({'Type': 'Term', 'name': {'$regex': '^(?!Tentative).*$', '$options': 'i'}}, {'abbrev': 1, '_id':0}).limit(1))[0]['abbrev']
        subj_abbrev_list = list(items.find({'Type': 'Subject'}, {'abbrev': 1, '_id':0}))

        urls = []
        #http://www.registrar.ucla.edu/schedule/detmain.aspx?termsel=13F&subareasel=COM+SCI
        for abbrev in subj_abbrev_list:
            #url = "http://www.registrar.ucla.edu/schedule/detmain.aspx?termsel={0}&subareasel={1}".format(current_term, abbrev['abbrev'].replace(" ","+"))
            class_number_list=list(items.find({'Type':'Class_Brief', 'subject':abbrev['abbrev']}, {'number': 1, '_id':0}))
            for class_number in class_number_list:
                
                url = "http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel={0}&subareasel={1}&idxcrs={2}".format(current_term, abbrev['abbrev'].replace(" ","+"), class_number['number'].replace(" ", "+"))

                urls.append(url)

        self.start_urls=urls

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

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


        EnrollTotals = hxs.select('//td[contains(@class, "EnrollTotal")]//span/text()').extract()
        EnrollCaps = hxs.select('//td[contains(@class, "EnrollCap")]//span/text()').extract()
        WaitListTotals = hxs.select('//td[contains(@class, "WaitListTotal")]//span/text()').extract()
        WaitListCaps = hxs.select('//td[contains(@class, "WaitListCap")]//span/text()').extract()
        Statuss = hxs.select('//td[contains(@class, "Status")]//span[@class="opengreen"]/text()').extract()
        ID_Numbers = hxs.select('//td[contains(@class, "IDNumber")]//a/@href').re('\d{9}')
        
        items=[]
        for i in range(len(EnrollTotals)):
            item = Class_Enrollment()
            item['subject_number'] = subject_number

            item['Type'] = 'Class_Enrollment'
            item['ID_number'] = ID_numbers[i]

            item['unique_key'] = ID_numbers[i]+item['Type']

            item['en_total'] = EnrollTotals[i]
            item['en_cap'] = EnrollCaps[i]
            item['WL_total'] = WaitListTotals[i]
            item['WL_Cap'] = WaitListCaps[i]
            item['status'] = Statuss[i]
            items.append(item)

        return items