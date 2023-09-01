from spider.base_spider import BaseSpider


try:
    from spider.base_spider import BaseParser, BaseSpider, CustomRequestTask
except ModuleNotFoundError as err:
    from base_spider import BaseParser, BaseSpider, CustomRequestTask


class MiParser(BaseParser):

    def __init__(self, spider: BaseSpider, debug: bool = False) -> None:
        super().__init__(spider, debug)

class MiSpider(BaseSpider):

    def __init__(self) -> None:
        super().__init__()

        self.register_parser(MiParser(self))


if __name__ == '__main__':
    pass