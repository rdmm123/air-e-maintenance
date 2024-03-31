# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging
from scrapy import Item, Spider

from src.services.telegram_api import TelegramAPIService, MessageFormat


class TelegramNotifyPipeline:
    def __init__(self) -> None:
        self.telegram_service = TelegramAPIService()

        with open('files/message_template.txt') as f:
            self.message_template = f.read()

        self.logger = logging.getLogger()

    def process_item(self, item: Item, spider: Spider):
        adapter = ItemAdapter(item)

        # Escape reserved values for Markdown
        fields_to_escape = ['date', 'url', 'reason', 'sector']
        chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for field in fields_to_escape:
            value = adapter.get(field)
            for char in chars_to_escape:
                value = value.replace(char, f'\\{char}')
            adapter[field] = value

        resp = self.telegram_service.send_message_to_me(
            self.message_template.format(**adapter), format=MessageFormat.MARKDOWN_V2)
        self.logger.info(f'Response from Telegram API: {resp}')

        return item
