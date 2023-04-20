# -*- coding: utf-8 -*-
"""module description
"""

import time
from urllib.parse import urlparse, parse_qs

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from front.twelS.settings import BASE_DIR
from twels.searcher.searcher import Searcher
from django.contrib.auth.decorators import login_required
from twels.mathpix.mathpix import mathocr


@login_required
def index(request: WSGIRequest):
    """サイトに最初にアクセスしたときや検索したときに呼び出される関数．
    """
    if request.method == 'GET':
        url_params = {
            'q': [],
            'start': [],
            'lr': []
        }

        # request.GET.get('q')をしてしまうと'%20'が' 'に
        # 変換されてしまうのでrequest.GET.get('q')などは使わない。
        full_path = request.get_full_path().replace('%20', '')
        url_params.update(parse_qs(urlparse(full_path).query))

        if not url_params['start']:
            url_params['start'].append('0')

        page_list: list[dict] = []

        # 検索時
        if url_params['q']:
            # parse_qs()で'+'が' 'に変換されてしまうので、それを修正
            url_params['q'] = url_params['q'][0].split(' ')

            start_time = time.time()
            # TODO: 複数のキーワード検索にも対応する。
            result = Searcher.search(
                url_params['q'][0], int(url_params['start'][0]), url_params['lr']
                )
            page_list = result['search_result']
            search_time = time.time() - start_time
            print(f'search time: {search_time}秒')

        context = {
            'page_list': page_list,
            'start': str(int(url_params['start'][0])+10),
            'ocr': '',
        }
        return render(request, 'search/index.html', context)

    elif request.method == 'POST':
        if request.FILES.get('uploadImage', False):
            uploadedImage: bytes = request.FILES['uploadImage'].read()
            ocr = mathocr(uploadedImage)
            if ocr is not False:
                ocr: str = ocr.replace('\\', '\\\\')
                context = {'ocr': ocr}
            else:
                context = {'ocr': ' '}
        else:
            context = {'ocr': ''}
        return render(request, 'search/index.html', context)

    else:
        print('GET,POST以外のHTTP methodでアクセスされました．HTTP method: ', request.method)
        context = {}
        return render(request, 'search/index.html', context)


@login_required
def privacy_policy(request):
    """プライバシーポリシーのページ．
    """
    return render(request, 'search/privacy_policy.html', {})


@login_required
def feedback(request):
    """問い合わせのページ"""
    context = {}
    return render(request, 'search/feedback.html', context)


@login_required
def report(request):
    """バグ報告・要望のページ"""
    context = {}
    return render(request, 'search/report.html', context)


@login_required
def input_example(request):
    """数式の入力例のページ"""
    context = {}
    return render(request, 'search/input_example.html', context)


@login_required
def robots_txt(request):
    """robots.txtを表示するための関数．
    """
    text = ''
    try:
        with open(f'{BASE_DIR}/search/static/search/robots.txt') as f:
            text = f.read()
    except Exception:
        text = 'error'
    return HttpResponse(text, content_type='text/plain')
