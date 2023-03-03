import os
import base64
import json

import requests
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env()


default_headers: dict[str, str] = {
    'app_id': env('MATHPIX_ID'),
    'app_key': env('MATHPIX_KEY'),
    'Content-type': 'application/json'
}

service: str = 'https://api.mathpix.com/v3/latex'


def latex(args: dict, headers: dict = default_headers) -> dict:
    """Call the Mathpix service with the given arguments and headers.
    Args:
        args: 画像のdataURLとレスポンス時にどのように結果を返すか等をdict型で指定.
        e.g.
        {
            'src': 'data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/4Q・・・',
            'ocr': ['math', 'text'],
            'formats': ['text', 'latex_styled'],
            ・・・
        }
        headers: api_id,api_keyと戻り値の型を指定する.
    Returns:
        dict型で書かれた画像データの識別結果.args次第で詳細に返す識別結果を設定できる.
        e.g.
        {
            'latex_confidence': 0.9660966,
            'mathml': '<math>・・・</math>',
            'text': 'How do you multiply \( \frac { 7 x } { 5 x + 15 }
                    \cdot \frac { x + 3 } { 8 } ?  \)',
            'latex_styled': '\( \frac { 7 x } { 5 x + 15 } \cdot
                            \frac { x + 3 } { 8 } ?  \)',
            ・・・
        }
    """
    encoded_data = json.dumps(args)
    ocr_response = requests.post(
        service, data=encoded_data, headers=headers, timeout=30)
    return json.loads(ocr_response.text)


def mathocr(image: bytes) -> str | bool:
    """mathpixにimageのOCRをリクエストし,レスポンスとしてOCRの結果を取得する関数.
    Arg:
        image: 画像ファイルアップローダーから取得した画像のバイナリデータ.
        e.g.
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01・・・'
    Return:
        latex形式の数式.または,数式認識が出来なかった場合のFalse.
        e.g.
        '\( \frac { 7 x } { 5 x + 15 } \cdot
        \frac { x + 3 } { 8 } ?  \)'
    """
    image_payload = base64.b64encode(image).decode()
    image_dataURL: str = f'data:image/jpg;base64,{image_payload}'
    ocr_response: dict = latex({
        'src': image_dataURL,
        'ocr': ['math'],
        'skip_recrop': True,
        'formats': ['latex_styled'],
        'format_options': {'latex_styled': {'transforms': ['rm_spaces']}}
    })

    # the formula is recognized.
    if 'latex_styled' in ocr_response:
        return ocr_response['latex_styled']

    # the formula is not recognized.
    else:
        return False
