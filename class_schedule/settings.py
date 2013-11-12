# Scrapy settings for class_schedule project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'class_schedule'

SPIDER_MODULES = ['class_schedule.spiders']
NEWSPIDER_MODULE = 'class_schedule.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'class_schedule (+http://www.yourdomain.com)'

#CONCURRENT_REQUESTS = 100
COOKIES_ENABLED = False

ITEM_PIPELINES = [
  'class_schedule.scrapymongodb.MongoDBPipeline',
]


# MONGODB_URI = 'mongodb://class:classTP@paulo.mongohq.com:10057/scrapy'
# MONGODB_DATABASE = 'scrapy'
# MONGODB_COLLECTION = 'items'

# MONGODB_URI = 'mongodb://127.0.0.1:3002/meteor'
# MONGODB_DATABASE = 'meteor'
# MONGODB_COLLECTION = 'items'
MONGODB_ADD_TIMESTAMP = True