# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Term(Item):
	unique_key = Field()	
	Type = Field()
	name = Field()
	abbrev = Field()
    
class Subject(Item):
	unique_key = Field()
	Type = Field()
	name = Field()
	abbrev = Field()

class Class(Item):
	unique_key = Field()
	Type = Field()

	subject_number = Field()
	subject = Field()
	number = Field()
	name_des = Field()

	ID_number = Field()
	lecture_number = Field()
	section_type = Field()
	section_number = Field()
	days = Field()
	start = Field()
	end = Field()
	building = Field()
	room = Field()
	restrict = Field()

	#ields that are to be frequently updated
	en_total = Field()
	en_cap = Field()
	WL_total = Field()
	WL_Cap = Field()
	status = Field()

	#fields that only lectures(ID ends with 0) have:
	name_short_des = Field()
	webpage = Field()
	lib_reserves = Field()
	textbooks = Field()
	crs_info = Field()
	final_exam = Field()

	#fields that need crs info page
	instructor = Field()

	class_title = Field()
	final_code = Field()
	final_location = Field()
	crs_des = Field()
	GE_status = Field()
	units = Field()
	grading_detail = Field()
	enforced_requisites = Field()
	Impacted = Field()
	enrollment_restriction = Field()
	consent_of_department = Field()
	material_use_fee = Field()
	instructional_enhancement_fee = Field()
	notes = Field()


class Class_Brief(Item):
	unique_key = Field()
	Type = Field()
	subject_number = Field()
	name_des = Field()
	subject = Field()
	number = Field()

class Error_in_Class_Spider(Item):
	unique_key = Field()
	ID_number = Field()
	Error = Field()

class Class_Detailed(Item):
	unique_key = Field()
	Type = Field()
	subject_number = Field()
	ID_number = Field()
	
	name_short_des = Field()
	webpage = Field()
	lib_reserves = Field()
	textbooks = Field()
	crs_info = Field()
	final_exam = Field()
	class_title = Field()
	final_code = Field()
	final_location = Field()
	crs_des = Field()
	GE_status = Field()
	units = Field()
	grading_detail = Field()
	enforced_requisites = Field()
	Impacted = Field()
	enrollment_restriction = Field()
	consent_of_department = Field()
	material_use_fee = Field()
	instructional_enhancement_fee = Field()
	notes = Field()

class Class_Schedule(Item):
	unique_key = Field() #id number
	Type = Field()
	subject_number = Field()
	lecture_number = Field()

	section_type = Field()
	section_number = Field()

	ID_number = Field()
	instructor = Field()
	days = Field()
	start = Field()
	end = Field()
	building = Field()
	room = Field()
	restrict = Field()

class Class_Enrollment(Item):
	unique_key = Field() #id number+en
	Type = Field()
	subject_number = Field()
	ID_number = Field()
	en_total = Field()
	en_cap = Field()
	WL_total = Field()
	WL_Cap = Field()
	status = Field()
