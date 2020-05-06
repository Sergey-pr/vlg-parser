# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from rotating_proxies.middlewares import RotatingProxyMiddleware

from scrapy import signals
from scrapy.exceptions import IgnoreRequest

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import get_meta_refresh


class VlgParserCrawlersSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class VlgParserCrawlersDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        # Must either:
        if 'captcha' in request.url:
            raise IgnoreRequest
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.
        if exception == IgnoreRequest:
            request.url = request.url.replace('https://volgograd.cian.ru/captcha/?redirect_url=', '')
            return request
        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CustomRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        log = spider.logger
        url = response.url
        if response.status in [301, 307]:
            log.info("trying to redirect us: %s" % url)
            reason = 'redirect %d' % response.status
            return self._retry(request, reason, spider) or response
        interval, redirect_url = get_meta_refresh(response)
        # handle meta redirect
        if redirect_url:
            log.info("trying to redirect us: %s" % url)
            reason = 'meta'
            return self._retry(request, reason, spider) or response
        if 'captcha' in request.url:
            log.info("captcha page %s" % url)
            reason = 'captcha'
            return self._retry(request, reason, spider) or response
        return response
