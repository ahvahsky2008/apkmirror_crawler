import scrapy
from apkmirror.items import ApkmirrorItem
from loguru import logger

class ApkmirrorSpider(scrapy.Spider):
    name = 'apkmirror_spider'
    allowed_domains = ['apkmirror.com']
    start_urls = ['https://www.apkmirror.com/uploads/page/1/']

    def parse(self, response):
        apk_links = response.xpath('//a[@class="fontBlack"]/@href').extract()[0:10]
        if apk_links:
            page_num = response.meta.get('page_num')
            if page_num is None:
                next_page_link = response.url + 'page/2/'
                page_num = 2
            else:
                page_num += 1
                splitted = response.url.split('/')[:5]
                splitted.append(str(page_num))
                next_page_link = '/'.join(splitted)
            
            if page_num != 3:
                yield response.follow(
                    next_page_link,
                    callback=self.parse,
                    meta={
                        'page_num': page_num,
                    },
                )
        
        for apk_link in apk_links:
            yield response.follow(
                apk_link,
                callback=self.parse_apk_details,
            )

    def parse_apk_details(self, response):
        apk_item = ApkmirrorItem()
        try:
            download_link =response.xpath("//div[contains(@class, 'table-cell rowheight addseparator expand pad dowrap')]/a/@href").extract()
            if not download_link:
                download_link = response.xpath("//a[contains(@class, 'accent_bg btn btn-flat downloadButton')]/@href").extract()[-1]
            else:
                download_link = download_link[-1]
                
            array_of_data = response.xpath(
                '//div[@class="infoSlide t-height"]/'
                'p/span[@class="infoSlide-value"]/text()').extract()
            
            if len(array_of_data) >= 4:
                for data in array_of_data[:4]:
                    if 'mb' in data.lower():
                        apk_item['file_size'] = data
                    elif 'gmt' in data.lower():
                        apk_item['uploaded'] = data
                    elif data.count('.') >= 2:
                        apk_item['version'] = data
                    else:
                        apk_item['downloads'] = data

            url ='https://www.apkmirror.com'+ download_link

            request =  scrapy.Request(url, self.parse_app_ur, meta={'item': apk_item})
            yield request
        except  Exception as e:
            logger.error(f'problem with url {response.url}')

    
    def parse_app_ur(self, response):
        try:
            url = response.xpath("//a[contains(@class, 'accent_bg btn btn-flat downloadButton')]/@href").extract_first()
            item = response.meta['item']
            item['download_link'] ='https://www.apkmirror.com'+ url
            yield item
        except:
            item = response.meta['item']
            item['download_link'] =response.url
            yield item
