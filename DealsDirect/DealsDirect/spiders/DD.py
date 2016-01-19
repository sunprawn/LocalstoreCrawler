__author__ = 'simony'
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from DealsDirect.items import DealsdirectItem
from DealsDirect import settings


class DDSpider(Spider):
    name = "DealsDirectCategories"
    allowed_domains = ["www.dealsdirect.com.au","dealsdirect.com.au"]
    start_urls = [
        "http://www.dealsdirect.com.au/%s/?sort=popularity&display=all&cachekey=48&lnk=catviewall" % s
        for s in settings.CATEGORIES
    ]

    def parse(self, response):
        for product in response.xpath('//ul[contains(@class,"dd-products-box")]/li'):
            link = product.xpath('ul/li/ul/li[@class="dd-product-title"]/a/@href').extract_first()

            if link is None:
                continue
            else:
                url = response.urljoin(link)
                #self.logger.info(url)
                yield Request(url, callback=self.parse_product)
        #yield Request(url, callback=self.parse_product)

        next_page = response\
            .xpath('//div[contains(@class, "pagination")]/ul/li[@class="arrow-next"]/a/@href')\
            .extract_first()

        #self.logger.info(next_page)

        if next_page:
            next_url = response.urljoin(next_page)
            #self.logger.info(next_url)
            yield Request(next_url, callback=self.parse)

    def parse_product(self, response):
        product = DealsdirectItem()

        product_info = response.xpath('//div[@class="dd-product-info"]')
        product_controls = product_info.xpath('//div[@class="productColLeftDescription"]')

        #product['title'] = product_info.xpath('//div[@id="dd-product-name"]/h1/span/text()').extract_first

        #get product ID
        product['product_id'] = int(product_controls.xpath('//input[@name="p"]/@value').extract_first())

        # get product quantity, and price
        # if product is not available i.e. out of stock
        if product_controls.xpath('//li[@class="dd-product-soldout"]'):
            product['quantity'] = 0
            product['product_id'] = int(product_controls.xpath('./input[@name="p"]/@value').extract_first())
            #product['sku'] = ''
        else:
            #product['sku'] = product_controls\
            #    .xpath('//li[@class="dd-product-quantity"]/input[@name="SKU"]/@value').extract_first()

            product['quantity'] = int(product_controls\
                .xpath('//li[@class="dd-product-quantity"]/label/select[@name="Quantity"]/option[last()]/@value')\
                .extract_first())
            product['price'] = float(product_controls\
                .xpath('//li[@class="dd-product-offer"]//span[@id="itemUnitPrice"]/text()').extract_first()[1:])
            price_original = product_controls\
                .xpath('//li[@class="dd-product-offer"]//span[@id="productPageOriginalPrice"]/span/text()').extract_first()
            if price_original:
                price_original = price_original.strip()
                product['price_original'] = float(price_original[1:])
            else:
                product['price_original'] = 0

        # get category and url
        product_categories_count = response.xpath('count(//section[@id="page-category"]/div/span)').extract_first()
        product_categories = response.xpath('//section[@id="page-category"]/div')

        category1 = product_categories.xpath("./span[2]/a/span/text()").extract_first()
        if int(float(product_categories_count)) == 4:
            category2 = product_categories.xpath("./span[3]/a/span/text()").extract_first()
        else:
            category2 = ""
        product['url'] = product_categories.xpath('./span[last()]/a/@href').extract_first()
        title = product_categories.xpath('./span[last()]/a/span/text()').extract_first()

        if title:
            product['title'] = title.strip()
        if category1:
            product['category1'] = category1.strip()
        if category2:
            product['category2'] = category2.strip()
        else:
            product['category2'] = ''

        # get product description
        product_details = product_info.xpath('.//div[@id="dd-description-tab-div"]')
        description_title = product_details.xpath('.//div[@class="brand-info"]/h2/text()').extract_first()
        description = product_details.xpath('.//div[@class="brand-more-info"]/node()').extract()

        if description_title:
            product['description_title'] = description_title.strip()
        if description:
            product['description'] = " ".join(description).replace("\n", "")

        sku = product_details.xpath('.//div[@class="product-code"]/text()').extract_first()
        if sku:
            product['sku'] = sku.replace("Product Code: ", "")
        else:
            product['sku'] = ""

        yield product