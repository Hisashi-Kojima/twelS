# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import time
from typing import Union

from django.http import HttpResponse
from django.shortcuts import render

from twelS.settings import BASE_DIR
from search.searcher.searcher import Searcher


def index(request):
    """サイトに最初にアクセスしたときや検索したときに呼び出される関数．
    """
    if request.method == 'GET':
        page_list: list[dict] = []
        result_num = 0

        expr: Union[str, None] = request.GET.get('q')
        if expr is not None and expr != '':
            start_time = time.time()
            result = Searcher.search(expr)
            page_list: list[dict] = result['search_result']
            result_num: int = result['result_num']
            search_time = time.time() - start_time
            print(f'search time: {search_time}秒')

        context = {
            'page_list': page_list,
            'result_num': result_num,
            'query': expr,
        }
    else:
        print('GET以外のHTTP methodでアクセスされました．HTTP method: ', request.method)
        context = {}
    return render(request, 'search/index.html', context)


def robots_txt(request):
    """robots.txtを表示するための関数．
    """
    text = ''
    with open(f'{BASE_DIR}/search/static/search/robots.txt') as f:
        text = f.read()
    return HttpResponse(text, content_type='text/plain')


def coming_soon(request):
    """公開前に表示するページ．
    """
    return render(request, 'search/coming_soon.html', {})
