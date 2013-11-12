from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from class_schedule.items import Term
from class_schedule.items import Subject


class Term_Subject_Spider(BaseSpider):
    name = "Term_Subject"
    allowed_domains = ["registrar.ucla.edu"]
    start_urls = [
        "http://www.registrar.ucla.edu/schedule/"
        ]

    def parse(self, response):
        sel = HtmlXPathSelector(response)
        term_names = sel.select('//option/text()').re('.*[0-9]{4}$')
        term_abbrevs = sel.select('//option/@value').re('^[0-9]{2}.$')
        items=[]
        for i in range(len(term_names)):
            item = Term()
            item['name'] = term_names[i]
            item['abbrev'] = term_abbrevs[i]
            item['Type'] = 'Term'
            item['unique_key'] = term_abbrevs[i]
            items.append(item)

        subject_names = sel.select('//option/text()').extract()
        subject_abbrevs = sel.select('//option/@value').extract()


        for i in range(len(subject_names)):
            if i < len(term_names):
                continue
            item = Subject()
            item['name'] = subject_names[i]
            item['abbrev'] = subject_abbrevs[i]
            item['Type'] = 'Subject'
            item['unique_key'] = subject_abbrevs[i]
            items.append(item)
        return items