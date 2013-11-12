from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Class
from pymongo import MongoClient
from scrapy import log
import re

class Class_Schedule_Second_Spider(BaseSpider):
    name = "Class_Second"
    allowed_domains = ["registrar.ucla.edu"]
    start_urls = []

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['scrapy-mongodb']
        items = db['items']

        current_term = list(items.find({'Type': 'Term', 'name': {'$regex': '^(?!Tentative).*$', '$options': 'i'}}, {'abbrev': 1, '_id':0}).limit(1))[0]['abbrev']
        ID_number = list(items.find({'Type': 'Class'},{'ID_number': 1, '_id':0}))

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
        unique_key = re.search('\d{9}', response.url).group(0)

        instructor = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblInstructor"]/text()').extract()
        instructor = instructor[0] if instructor else None

        if unique_key[-1]!="0":
            items.update({'unique_key': unique_key},{'$set':{
                'instructor': instructor
                } })
            return

        class_title = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblClassTitle"]/text()').extract()
        final_code = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblFinalExam"]/text()').extract()
        crs_des = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblCourseDescription"]/text()').extract()
        GE_status = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblGEStatus"]/text()').extract()
        units = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblUnits"]/text()').extract()
        grading_detail = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblGradingDetail"]/text()').extract()
        enforced_requisites = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblEnforcedReq"]/text()').extract()
        Impacted = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblImpacted"]/text()').extract()
        enrollment_restriction = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblEnrollRestrict"]/text()').extract()
        consent_of_department = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblConsentReq"]/text()').extract()
        material_use_fee = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblMaterialFee"]/text()').extract()
        instructional_enhancement_fee = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblEnhancementFee"]/text()').extract()
        notes = hxs.select('//span[@id="ctl00_BodyContentPlaceHolder_subdet_lblNotes"]/text()').extract()
        class_title = class_title[0] if class_title else None
        final_code = final_code[0] if final_code else None
        crs_des = crs_des[0] if crs_des else None
        GE_status = GE_status[0] if GE_status else None
        units = units[0] if units else None        
        grading_detail = grading_detail[0] if grading_detail else None
        enforced_requisites = enforced_requisites[0] if enforced_requisites else None        
        Impacted = Impacted[0] if Impacted else None
        enrollment_restriction = enrollment_restriction[0] if enrollment_restriction else None
        consent_of_department = consent_of_department[0] if consent_of_department else None
        material_use_fee = material_use_fee[0] if material_use_fee else None
        instructional_enhancement_fee = instructional_enhancement_fee[0] if instructional_enhancement_fee else None
        notes = notes[0] if notes else None


        items.update({'unique_key': unique_key},{'$set':{
            'instructor': instructor,

            'class_title': class_title,
            'final_code': final_code,
            'crs_des': crs_des,
            'GE_status': GE_status,
            'units': units,
            'grading_detail': grading_detail,
            'enforced_requisites': enforced_requisites,
            'Impacted': Impacted,
            'enrollment_restriction': enrollment_restriction,
            'consent_of_department': consent_of_department,
            'material_use_fee': material_use_fee,
            'instructional_enhancement_fee': instructional_enhancement_fee,
            'notes': notes
            } })