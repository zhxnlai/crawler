from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class
from pymongo import MongoClient
from scrapy import log
import re

#depends on Class_Brief
class Class_Spider(BaseSpider):
    name = "Class"
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

        #schedule
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

        ##### Enrolls ####
        EnrollTotals = hxs.select('//td[contains(@class, "EnrollTotal")]//span/text()').extract()
        EnrollCaps = hxs.select('//td[contains(@class, "EnrollCap")]//span/text()').extract()
        WaitListTotals = hxs.select('//td[contains(@class, "WaitListTotal")]//span/text()').extract()
        WaitListCaps = hxs.select('//td[contains(@class, "WaitListCap")]//span/text()').extract()
        Statuss = hxs.select('//td[contains(@class, "Status")]/span[contains(@id, "ctl00_BodyContentPlaceHolder_detselect")]//span/text()').extract()

        #Details
        name_short_des = hxs.select('//tr[@class="SAHeaderDarkGreenBar"]/td/span[contains(@id, "CourseHead")][@class="coursehead"]/text()').extract()
        webpage = hxs.select('//a[contains(text(), "Course Webpage")]/@href').extract()
        lib_reserves = hxs.select('//a[contains(text(), "Library Reserves")]/@href').extract()
        textbooks = hxs.select('//a[contains(text(), "Textbooks")]/@href').extract()
        final_exam = hxs.select('//a[contains(text(), "Final Examination")]/@href').extract()
        crs_info = hxs.select('//a[contains(text(), "Crs Info")]/@href').extract()



        index_of_subject =response.url.find('subareasel=')+len('subareasel=')
        index_of_number= response.url.find('&idxcrs=')+len('&idxcrs=')
        subj = response.url[index_of_subject:index_of_number-len('&idxcrs=')]
        num = response.url[index_of_number:]
        subj = subj.replace("+", " ")
        num = num.replace("+", " ")#this number is special
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']

        #brief
        from_brief = list(items.find({'Type':'Class_Brief', 'subject': subj, 'number': num}, {'subject_number':1, 'name_des':1, '_id':0}))
        subject_number = from_brief[0]['subject_number']
        name_des = from_brief[0]['name_des']
        #lecturer


        items=[]
        for j in range(len(lecture_numbers)):
            for k in range(len(IDNumbers)):
                i = k+j*len(IDNumbers)
                item = Class()
                item['Type'] = 'Class'
                item['subject_number'] = subject_number
                item['subject'] = subj
                item['number'] = num
                item['name_des'] = name_des

                item['ID_number'] = IDNumbers[i] if IDNumbers[i] else None
                item['lecture_number'] = lecture_numbers[j] if lecture_numbers[j] else None
                item['section_type'] = Types[i] if Types[i] else None   
                item['section_number'] = SectionNumbers[i] if SectionNumbers[i] else None
                item['days'] = Dayss[i] if Dayss[i] else None
                item['start'] = TimeStarts[i] if TimeStarts[i] else None
                item['end'] = TimeEnds[i] if TimeEnds[i] else None
                item['building'] = Buildings[i] if Buildings[i] else None
                item['room'] = Rooms[i] if Rooms[i] else None
                item['restrict'] = Restricts[i] if Restricts[i] else None

                item['en_total'] = EnrollTotals[i] if EnrollTotals[i] else None
                item['en_cap'] = EnrollCaps[i] if EnrollCaps[i] else None
                item['WL_total'] = WaitListTotals[i] if WaitListTotals[i] else None
                item['WL_Cap'] = WaitListCaps[i] if WaitListCaps[i] else None
                item['status'] = Statuss[i] if Statuss[i] else None


                item['unique_key'] = IDNumbers[i] if IDNumbers[i] else None

                if item['ID_number'][-1]=="0":
                    item['name_short_des'] = name_short_des[0] if name_short_des else None
                    item['webpage'] = webpage[0] if webpage else None
                    item['lib_reserves'] = lib_reserves[0] if lib_reserves else None
                    item['textbooks'] = textbooks[0] if textbooks else None
                    item['final_exam'] = final_exam[0] if final_exam else None

                    if crs_info:
                        item['crs_info'] = crs_info[0]
                        url_split = response.url.split("/")
                        url_split[-1]=item['crs_info']
                        item['crs_info'] = "/".join(url_split)
                    else:
                        IDNumberss = hxs.select('//td[contains(@class, "IDNumber")]//a/@href').extract()
                        if IDNumberss:
                            item['crs_info'] = IDNumbers[0]
                            url_split = response.url.split("/")
                            url_split[-1]=item['crs_info']
                            item['crs_info'] = "/".join(url_split)
                    pass

                items.append(item)

        return items


    #def from_brief(self, response)