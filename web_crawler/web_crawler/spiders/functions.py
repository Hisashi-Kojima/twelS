# -*- coding: utf-8 -*-
"""functions for spiders.
"""
import json
import re

from bs4 import BeautifulSoup, Comment
import requests
from scrapy.utils.httpobj import urlparse


def get_lang(response) -> str:
    """ページの設定言語を取得する関数．"""
    return response.xpath('/html/@lang').get()


def get_title(response) -> str:
    """ページのタイトルを取得する関数．"""
    return response.css('title::text').get()


def get_snippet(response) -> str:
    """ページの説明を取得する関数．
    TODO:
        登録できる文字のmax lengthを設定して，それに収まっているかを確認する．
    """
    # TODO: spiderのコードの中でBeautifulSoupに置き換えられる場所があるか検討
    # 参考: https://doc.scrapy.org/en/latest/faq.html#can-i-use-scrapy-with-beautifulsoup
    body = response.css('body').get()
    return _clean_text(body)


def get_domain_from_uri(uri: str) -> str:
    """URIからドメインを抽出して返す関数．"""
    parseResult = urlparse(uri)
    return f'{parseResult.scheme}://{parseResult.netloc}'


def get_exprs(response) -> list[str]:
    """ページの式のリストを返す関数．"""
    result = []
    for mathml in response.xpath('//math').getall():
        tmp = _remove_indent_and_new_line(mathml)

        # _clean_textの方と合わせるためにBeautifulSoupを使う
        soup = BeautifulSoup(tmp, 'lxml')
        # 補完されるhtmlタグとbodyタグを削除
        soup.html.unwrap()
        soup.body.unwrap()

        _remove_comments(soup)
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


def _clean_text(text: str) -> str:
    """不要なタグなどを削除する関数．
    不要な情報を削除することで，登録するデータ量を小さくする．
    classなどが自作のものとかぶっても困るので，そのあたりの削除．
    """
    soup = BeautifulSoup(text, 'lxml')
    soup.html.unwrap()
    soup.body.unwrap()
    for a in soup.find_all('a'):
        a.unwrap()
    for b in soup.find_all('b'):
        b.unwrap()
    for i in soup.find_all('i'):
        i.unwrap()
    for p in soup.find_all('p'):
        p.unwrap()
    for div in soup.find_all('div'):
        div.unwrap()
    for span in soup.find_all('span'):
        span.unwrap()
    for dl in soup.find_all('dl'):
        dl.unwrap()
    for dt in soup.find_all('dt'):
        dt.unwrap()
    for dd in soup.find_all('dd'):
        dd.unwrap()
    for table in soup.find_all('table'):
        table.decompose()
    for ol in soup.find_all('ol'):
        ol.decompose()
    for ul in soup.find_all('ul'):
        ul.decompose()
    for label in soup.find_all('label'):
        label.decompose()
    for h in soup.find_all(re.compile('h[1-6]')):
        h.decompose()
    for br in soup.find_all('br'):
        br.decompose()
    for img in soup.find_all('img'):
        img.decompose()
    for form in soup.find_all('form'):
        form.decompose()
    for input_ in soup.find_all('input'):
        input_.decompose()
    for button in soup.find_all('button'):
        button.decompose()
    for script in soup.find_all('script'):
        script.decompose()
    for footer in soup.find_all('footer'):
        footer.decompose()
    for nav in soup.find_all('nav'):
        nav.decompose()
    _remove_comments(soup)

    result = str(soup)
    return result.replace('\n', '')


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


def _remove_comments(soup: BeautifulSoup):
    """HTMLのコメントを削除する関数．
    """
    for comment in soup(text=lambda x: isinstance(x, Comment)):
        comment.extract()


def _remove_indent_and_new_line(text: str):
    """インデントと改行を削除する関数．
    """
    return ''.join(line.strip() for line in text.split('\n'))
