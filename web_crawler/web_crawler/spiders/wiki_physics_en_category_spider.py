# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class WikiPhysicsCategorySpider(CrawlSpider):
    # type 'scrapy crawl wiki_physics_en_category' to crawl.
    name = 'wiki_physics_en_category'
    allowed_domains = [
        'en.wikipedia.org',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DEPTH_LIMIT': 8,
    }

    start_urls = [
        # 物理に関する記事の一覧
        'https://en.wikipedia.org/wiki/Category:Physics',

        # Category:Physical_systemsのMachinesの中で数式があるのものを抜粋
        'https://en.wikipedia.org/wiki/Category:Clocks',
        'https://en.wikipedia.org/wiki/Category:Engines',
        'https://en.wikipedia.org/wiki/Category:Kinematics',
        'https://en.wikipedia.org/wiki/Category:Simple_machines',
    ]

    category_path = 'wiki/Category:'
    next_page = '/w/index'
    rules = (
        # extract category links to crawl all categories.
        Rule(
            LinkExtractor(
                allow=(category_path, next_page),
                restrict_xpaths=([
                    '//div[@id="mw-subcategories"]',
                ]),
                deny=([
                    # Category:Physicsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Physicists',
                    'https://en.wikipedia.org/wiki/Category:Physics_awards',
                    'https://en.wikipedia.org/wiki/Category:Physics_by_country',
                    'https://en.wikipedia.org/wiki/Category:Physics_events',
                    'https://en.wikipedia.org/wiki/Category:Physics_literature',
                    'https://en.wikipedia.org/wiki/Category:Physical_modeling',
                    'https://en.wikipedia.org/wiki/Category:Physics_organizations',
                    'https://en.wikipedia.org/wiki/Category:Works_about_physics',
                    'https://en.wikipedia.org/wiki/Category:Physics_stubs',

                    # Category:History_of_physicsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Books_about_the_history_of_physics',
                    'https://en.wikipedia.org/wiki/Category:History_of_electrical_engineering',
                    'https://en.wikipedia.org/wiki/Category:History_of_physics_journals',
                    'https://en.wikipedia.org/wiki/Category:Manhattan_Project',
                    'https://en.wikipedia.org/wiki/Category:Modern_physics',
                    'https://en.wikipedia.org/wiki/Category:History_of_optics',
                    'https://en.wikipedia.org/wiki/Category:Historical_physics_publications',
                    'https://en.wikipedia.org/wiki/Category:History_of_thermodynamics',
                    'https://en.wikipedia.org/wiki/Category:Physics_timelines',

                    # Category:Physics-related_listsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Indexes_of_physics_articles',
                    'https://en.wikipedia.org/wiki/Category:Lists_of_Solar_System_objects',
                    'https://en.wikipedia.org/wiki/Category:Lists_of_things_named_after_physicists',
                    'https://en.wikipedia.org/wiki/Category:Physics_timelines',

                    # Category:Physical_systemsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Machines',
                    'https://en.wikipedia.org/wiki/Category:Transport',
                ]),
            )
        ),

        # extract page links to download.
        Rule(
            LinkExtractor(
                allow=('wiki/Category:'),
                restrict_xpaths=([
                    '//*[@id="mw-normal-catlinks"]',
                ]),
                deny=([
                    # Category:Physicsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Physicists',
                    'https://en.wikipedia.org/wiki/Category:Physics_awards',
                    'https://en.wikipedia.org/wiki/Category:Physics_by_country',
                    'https://en.wikipedia.org/wiki/Category:Physics_events',
                    'https://en.wikipedia.org/wiki/Category:Physics_literature',
                    'https://en.wikipedia.org/wiki/Category:Physical_modeling',
                    'https://en.wikipedia.org/wiki/Category:Physics_organizations',
                    'https://en.wikipedia.org/wiki/Category:Works_about_physics',
                    'https://en.wikipedia.org/wiki/Category:Physics_stubs',

                    # Category:History_of_physicsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Books_about_the_history_of_physics',
                    'https://en.wikipedia.org/wiki/Category:History_of_electrical_engineering',
                    'https://en.wikipedia.org/wiki/Category:History_of_physics_journals',
                    'https://en.wikipedia.org/wiki/Category:Manhattan_Project',
                    'https://en.wikipedia.org/wiki/Category:Modern_physics',
                    'https://en.wikipedia.org/wiki/Category:History_of_optics',
                    'https://en.wikipedia.org/wiki/Category:Historical_physics_publications',
                    'https://en.wikipedia.org/wiki/Category:History_of_thermodynamics',
                    'https://en.wikipedia.org/wiki/Category:Physics_timelines',

                    # Category:Physics-related_listsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Indexes_of_physics_articles',
                    'https://en.wikipedia.org/wiki/Category:Lists_of_Solar_System_objects',
                    'https://en.wikipedia.org/wiki/Category:Lists_of_things_named_after_physicists',
                    'https://en.wikipedia.org/wiki/Category:Physics_timelines',

                    # Category:Physical_systemsの中の数式がないCategoryは除外
                    'https://en.wikipedia.org/wiki/Category:Machines',
                    'https://en.wikipedia.org/wiki/Category:Transport',
                ]),
            ),
            callback='parse'
        ),
    )

    # Get wiki category links
    def parse(self, response: TextResponse) -> scrapy.Item:
        with open("web_crawler/spiders/category.txt", "a", encoding='utf-8',newline="\n") as file:
            file.write(response.url),
            file.write("\n"),
