# -*- coding: utf-8 -*-
"""functions for spiders.
"""
import json
import re

from bs4 import BeautifulSoup
import requests
from scrapy.utils.httpobj import urlparse

from twels.indexer.snippet import Snippet


def get_lang(response) -> str:
    """ページの設定言語を取得する関数．"""
    return response.xpath('/html/@lang').get()


def get_title(response) -> str:
    """ページのタイトルを取得する関数．"""
    return response.css('title::text').get()


def get_snippet(response) -> Snippet:
    """ページの説明を取得する関数．
    """
    # TODO: spiderのコードの中でBeautifulSoupに置き換えられる場所があるか検討
    # 参考: https://doc.scrapy.org/en/latest/faq.html#can-i-use-scrapy-with-beautifulsoup
    body = response.css('body').get()
    return Snippet(body)


def get_domain_from_uri(uri: str) -> str:
    """URIからドメインを抽出して返す関数．"""
    parseResult = urlparse(uri)
    return f'{parseResult.scheme}://{parseResult.netloc}'


def get_exprs(response) -> list[str]:
    """ページの式のリストを返す関数．"""
    result = []
    for mathml in response.xpath('//math').getall():
        tmp = Snippet.remove_spaces(mathml)

        # Snippetの_clean_textの方と合わせるためにBeautifulSoupを使う
        soup = BeautifulSoup(tmp, 'lxml')
        # 補完されるhtmlタグとbodyタグを削除
        soup.html.unwrap()
        soup.body.unwrap()

        Snippet._remove_comments(soup)
        result.append(str(soup))
    return result


def render_katex(expr_katex: str) -> str:
    """KaTeXをMathMLに変換する関数。
    I don't use this function now, but I maybe use this in the future.
    Args:
        expr_katex: KaTeXで書かれた数式。
        ex. a+b, $a+b$, $$a+b$$
    Returns:
        MathML.
    Note:
        This function calls AWS Lambda function.
        Do not call too much this function,
        because if you calls this function too much,
        the price of AWS Lambda is expensive.
    """
    url = "https://vl1wuswquk.execute-api.ap-northeast-1.amazonaws.com/renderKatex"
    data = json.dumps({'expr': expr_katex})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=data, headers=headers)
    return _clean_mathml(response.text)


def render_katex_page(text: str) -> str:
    """KaTeXで書かれた数式を含んだ文章をMathMLで書かれた数式を含んだ文章に変換する関数。
    I don't use this function now, but I maybe use this in the future.
    Args:
        KaTeXで書かれた数式を含んだ文章。
    Returns:
        KaTeXで書かれた数式がrenderされた文章。
    Note:
        textのサイズが大きくなるとre.findall()にかかる時間がとても長くなり、
        render_katex_page()の処理が終わらないように見える。
    """
    result = text

    # render $$expr$$
    # use "?:" because non-capture version of regular parentheses is better here.
    katex_list: list[str] = re.findall(r'\$\$(?:.|\s)+\$\$', result)

    for katex in katex_list:
        mathml = render_katex(katex.strip('$'))
        result = result.replace(katex, mathml)

    # render $expr$
    katex_list: list[str] = re.findall(r'\$.+?\$', result)

    for katex in katex_list:
        mathml = render_katex(katex.strip('$'))
        result = result.replace(katex, mathml)

    return result


def _clean_mathml(response_text: str) -> str:
    """KaTeXをrenderした結果から不要なタグを削除する関数。
    I don't use this function now, but I maybe use this in the future.
    """
    # remove double quotes on both ends.
    text = response_text.strip('"')
    # remove all span tags.
    soup = BeautifulSoup(text, 'lxml')
    soup.html.unwrap()
    soup.body.unwrap()
    for span in soup.find_all('span'):
        span.unwrap()
    return str(soup)
