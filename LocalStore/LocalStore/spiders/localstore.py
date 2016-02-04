# -*- coding: utf-8 -*-
import re
from scrapy import Request, Spider, exceptions
from LocalStore.items import SuburbItem, StoreItem

class LocalstoreSpider(Spider):
    name = "localstore"
    allowed_domains = ["localstore.com.au", "www.localstore.com.au"]
    start_urls = [
        'http://www.localstore.com.au/browse/suburbs/%s/' % s
        for s in "mnopqrstuvwxyz"#"abcdefghijklmnopqrstuvwxyz"
    ]

    def parse(self, response):
        for suburb in response.css('.overviewlistlabel a'):
            title = suburb.xpath('./@title').extract_first()
            href = suburb.xpath('./@href').extract_first()

            if href:
                #if title == "Arana Hills, QLD": # @testing
                    #yield Request(response.urljoin(href), callback=self.parse_suburb)
                yield Request(response.urljoin(href), callback=self.parse_suburb)
                #self.logger.info(href)
                continue

        # get next page
        next_page = response.xpath('//div[contains(@class,"numpadactive")]/following-sibling::div[1]/a/@href').extract_first()
        if next_page:
            yield Request(response.urljoin(next_page), callback=self.parse)


    def parse_suburb(self, response):
        url = response.request.url
        suburb_id = re.search('.*\/(\d+)\/.*', url).group(1)
        page_id = re.search('.*\/(p(\d+))?', url).group(2)
        content = response.xpath('//table[contains(@class, "main_content")]//table//table//table')

        # first page, store suburb into database
        if not page_id or page_id == "1":

            location = content.xpath('./tr[1]//table/tr[2]/td/h3/b[last()]/text()').extract_first()

            if location:
                suburbRec = SuburbItem()
                suburb, state = location.split(",")
                suburbRec['id'] = suburb_id
                suburbRec['name'] = suburb.strip()
                suburbRec['state'] = state.strip()
                yield suburbRec

        for store_path in content.xpath('./tr[2]/td/table/tr'):
            href = store_path.xpath('./td[3]/h2/a/@href').extract_first()
            if href:
                yield Request(response.urljoin(href), callback=self.parse_shop, meta={'suburb': suburb_id})
                #self.logger.info(href)

        next_page_shop = content.xpath('./tr[3]/td/table/tr//a[text()="Next"]/@href').extract_first()
        if next_page_shop:
            yield Request(response.urljoin(next_page_shop), callback=self.parse_suburb)


    def parse_shop(self, response):
        intro = response.xpath('//h2[@class="Intro"]/text()').extract_first()
        if "Shopping Centre" in intro:
            detail_url = response.request.url.replace("/store/", "/map/", 1)
            yield Request(detail_url, callback=self.parse_shopping_centre_detail, meta=response.meta)
        else:
            store = StoreItem()
            categories = {}
            id = re.search('.*\/store\/(\d+)\/.*', response.request.url).group(1)
            name = response.xpath('//span[@itemprop="name"]/text()').extract_first()
            #address = response.xpath('//span[@itemprop="address"]/text()').extract_first()
            street_address = response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first()
            suburb = response.meta['suburb']
            state = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
            postcode = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()
            website = response.xpath('//div[@class="listing_content"]/div/div[@class="box"]/meta/following-sibling::table/tr/td[2]/a/@href').extract_first()

            phone = response.xpath('//div[contains(@class,"listing_header_details")]/table/tr/td[2]/b/text()').extract_first()

            opentime_str = ""
            for opentime in response.xpath('//div[contains(@class,"opentimes_box")]/div'):
                opentime_record_day = opentime.xpath('./div[@class="float_left"]/text()').extract_first()
                opentime_record_time = opentime.xpath('./div[@class="float_right"]/text()').extract_first()

                if opentime_record_day and opentime_record_time:
                    opentime_str = opentime_str + "|" + opentime_record_day.strip() + "," + opentime_record_time.strip()

            for category in response.xpath('//div[contains(@class,"categories_box")]/span'):
                c_url = category.xpath('./a/@href').extract_first()
                c_name = category.xpath('./a/text()').extract_first()
                c_id = re.search('.*\/(\d+)\/\d+\/.*', c_url).group(1)
                categories[c_id] = c_name

            shoppingcentre_url = response.xpath('//span[@itemprop="address"]/a[1]/@href').extract_first()
            if shoppingcentre_url:
                shoppingcentre_id = re.search('.*\/store\/(\d+)\/.*', shoppingcentre_url).group(1)
            else:
                shoppingcentre_id = None

            brand_info = response.xpath('//div[@class="listing_content"]/div/div[@class="box"]/a[last()]')
            brand_name = brand_info.xpath('./text()').extract_first()
            brand_img = response.xpath('//div[contains(@class, "listing_header_logo")]//img/@src').extract_first()
            if brand_img:
                #download the image
                pass
            else:
                brand_img = ""

            if brand_name and "locations" in brand_name:
                brand = brand_name.replace(' locations', '')
                b_id = brand_info.xpath('./@href').extract_first()
                b_id = re.search('.*\/stores\/(\d+)\/.*', b_id).group(1)
                store['brand'] = [{b_id: brand}, {"img": brand_img}]
            else:
                store['brand'] = None

            store['id'] = id
            store['name'] = name.strip()
            #if address:
                #store['address'] = address.strip()
            #else:
                #store['address'] = ""

            if street_address:
                store['street_address'] = street_address.strip()
            else:
                store['street_address'] = ""

            store['suburb'] = suburb

            if postcode:
                store['postcode'] = postcode.strip()
            else:
                store['postcode'] = ""

            if state:
                store['state'] = state.strip()
            else:
                store['state'] = ""

            if website:
                store['website'] = website.strip()
            else:
                store['website'] = ""

            if phone:
                store['phone'] = phone.strip()
            else:
                store['phone'] = ""

            if shoppingcentre_id:
                store['shopping_centre'] = shoppingcentre_id
            else:
                store['shopping_centre'] = ""

            store['categories'] = categories
            store['opentime'] = opentime_str

            yield store

    def _parse_shopping_centre(self, response):
        url = response.request.url
        page_id = re.search('.*\/(p(\d+))?', url).group(2)
        store_id = re.search('.*\/store\/(\d+)\/.*', url).group(1)
        self.logger.info("in shopping centre: " + url)
        # first page, make another request to parse shopping centre
        if not page_id or page_id == "1":
            detail_url = url.replace("/store/", "/map/", 1)
            yield Request(detail_url, callback=self.parse_shopping_centre_detail, meta=response.meta)

        content = response.xpath('//table[contains(@class, "main_content")]//table//table/tr/td[1]')
        # add shopping centre id to each store in it
        response.meta['shopping_centre'] = store_id

        #for store_path in content.xpath('./table[2]/tr'):
        #    href = store_path.xpath('./td[3]/h2/a/@href').extract_first()
        #    if href:
        #        self.logger.info("in shopping centre: " + href)
        #        yield Request(response.urljoin(href), callback=self.parse_shop, meta=response.meta)

        # crawl next page
        #next_page_shop = content.xpath('./table[3]/tr//a[text()="Next"]/@href').extract_first()
        #if next_page_shop:
        #    yield Request(response.urljoin(next_page_shop), callback=self._parse_shopping_centre)


    def parse_shopping_centre_detail(self, response):
        url = response.request.url
        store_id = re.search('.*\/map\/(\d+)\/.*', url).group(1)

        title = response.xpath('//title/text()').extract_first()
        name, _, address = title.split('-', 2)
        street_address, _, state = address.split(',', 2)

        content = response.xpath('//table[contains(@class, "main_content")]//table//table/tr/td[1]')

        phone = content.xpath('.//div[contains(@class, "listing_header_details")]/table/tr/td[2]/b/text()').extract_first()

        shopping_centre = StoreItem()
        shopping_centre['id'] = store_id
        shopping_centre['name'] = name.strip()
        shopping_centre['street_address'] = street_address.strip()
        shopping_centre['suburb'] = response.meta['suburb']
        shopping_centre['state'] = state.strip()

        if phone:
            shopping_centre['phone'] = phone.strip()
        else:
            shopping_centre['phone'] = ""

        shopping_centre['shopping_centre'] = "1"
        shopping_centre['website'] = ""
        shopping_centre['postcode'] = ""
        shopping_centre['brand'] = None
        shopping_centre['categories'] = {"329":"Shopping Centre"}
        shopping_centre['opentime'] = ""

        yield shopping_centre