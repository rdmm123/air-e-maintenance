from typing import Any, Iterable
import scrapy
import datetime as dt
from scrapy.http import HtmlResponse
from scrapy import Request

from src.items import AireMaintenanceItem

class AireMaintenanceSpider(scrapy.Spider):
    name = "aire_maintenance"
    allowed_domains = ["air-e.com"]
    START_URL = "https://www.air-e.com/hogares/mi-energia/mantenimiento-programado/acat/2/date/{date}-1"
    days_to_check: int = None
    kw_for_lookup: str = None

    def __init__(self, name: str | None = None, **kwargs: Any):
        required_additional_kwargs = ['days_to_check', 'kw_for_lookup']

        for kwarg in required_additional_kwargs:
            if kwarg not in kwargs:
                raise Exception(f'Missing required kwarg: {kwarg}')
            
            setattr(self, kwarg, kwargs[kwarg])
            del kwargs[kwarg]

        self.days_to_check = int(self.days_to_check)
            
        super().__init__(name, **kwargs)

    def start_requests(self) -> Iterable[Request]:
        today = dt.datetime.today().strftime('%-d-%-m-%Y')
        return [Request(self.START_URL.format(date=today))]

    def get_dates_to_check(self):
        start = dt.datetime.today()
        dates = []

        for i in range(self.days_to_check):
            date = start + dt.timedelta(days=i + 1)
            dates.append(date.strftime('%-d-%-m-%Y'))

        return dates       

    def parse(self, response: HtmlResponse):
        dates_to_check = self.get_dates_to_check()
        self.logger.info('Checking for maintenance on the following dates:'
                         f'{dates_to_check}')

        for date in dates_to_check:
            date_td = response.xpath(
                f"//td[a[contains(@href, 'date/{date}')]]")
            
            # Could update this to make it dynamic, not hard-coded
            atlantico_maintenance = date_td.xpath(
                ".//a[contains(text(), 'Atlántico')]/@href").get()

            if not atlantico_maintenance:
                self.logger.info(f'No maintenances scheduled for {date}')
                continue
            
            yield response.follow(atlantico_maintenance, self.parse_maintenance)
        
    def parse_maintenance(self, response: HtmlResponse):
        table = response.css('div.article.details table tbody')
        rows = table.xpath(f".//tr[td[contains(text(), '{self.kw_for_lookup}')]]")

        if not rows.get():
            self.logger.info('Lookup keyword not found in maintenances for '
                             f'url: {response.url}')
            return None
        
        for row in rows:
            _, _, date, start, end, reason, sector, _ = row.css('td ::text').getall()
            
            item = AireMaintenanceItem()
            item['date'] = date
            item['start'] = start
            item['end'] = end
            item['reason'] = reason
            item['sector'] = sector
            item['url'] = response.url

            yield item