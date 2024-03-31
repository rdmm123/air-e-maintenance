from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# This could be read from env vars
DAYS_TO_CHECK = 7
KEYWORD_FOR_LOOKUP = "FLORESTA"

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    process.crawl('aire_maintenance',
                days_to_check=DAYS_TO_CHECK,
                kw_for_lookup=KEYWORD_FOR_LOOKUP)
    process.start()