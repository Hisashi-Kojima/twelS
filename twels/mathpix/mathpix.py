import os
import base64
import json

import requests
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env()


default_headers: dict = {
    'app_id': env('MATHPIX_ID'),
    'app_key': env('MATHPIX_KEY'),
    'Content-type': 'application/json'
}

service: str = 'https://api.mathpix.com/v3/latex'


def latex(args: dict, headers: dict = default_headers) -> dict:
    """Call the Mathpix service with the given arguments, headers, and timeout.
    Args:
        args: 画像のdataURLとレスポンス時にどのように結果を返すか等をdict型で指定.
        headers: api_id,api_keyと戻り値の型を指定する.
        timeout: POSTrequestの際のtimeout時間の設定.
    Returns:
        dict型で書かれた画像データの識別結果.args次第で詳細に返す識別結果を設定できる.
    """
    encoded_data: dict = json.dumps(args)
    ocr_response: requests.models.Response = requests.post(
        service, data=encoded_data, headers=headers, timeout=30)
    return json.loads(ocr_response.text)


def mathocr(image: bytes) -> str:
    """mathpixにimageのOCRをリクエストし,レスポンスとしてOCRの結果を取得する関数.
    Arg:
        image: 画像ファイルアップローダーから取得した画像のバイナリデータ.
    Return:
        latex形式の数式．もしくは，識別できなかった旨の文字列．
    """
    image_payload: str = base64.b64encode(image).decode()
    image_dataURL: str = f'data:image/jpg;base64,{image_payload}'
    ocr_response: dict = latex({
        'src': image_dataURL,
        'ocr': ['math', 'text'],
        'skip_recrop': True,
        'formats': [
            'text',
            'latex_styled',
            'asciimath',
            'mathml'
        ],
        'format_options': {
            'text': {
                'transforms': ['rm_spaces', 'rm_newlines'],
                'math_delims': ['$', '$']
            },
            'latex_styled': {'transforms': ['rm_spaces']}
        }
    })

    # the formula recognized
    if ocr_response['detection_map']['is_not_math'] == 0:
        return ocr_response['latex_styled']

    # the formula not recognized
    else:
        return "Not Recognized"
