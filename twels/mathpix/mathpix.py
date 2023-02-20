import os
import base64
import requests
import json

import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env()


#
# Common module for calling Mathpix OCR service from Python.
#
# N.B.: Set your credentials in environment variables APP_ID and APP_KEY,
# either once via setenv or on the command line as in
# APP_ID=my-id APP_KEY=my-key python3 simple.py 
#

default_headers = {
    'app_id': env('APP_ID'),
    'app_key': env('APP_KEY'),
    'Content-type': 'application/json'
}

service = 'https://api.mathpix.com/v3/latex'

#
# Call the Mathpix service with the given arguments, headers, and timeout.
#
def latex(args, headers=default_headers, timeout=30):
    r = requests.post(service,
        data=json.dumps(args), headers=headers, timeout=timeout)
    return json.loads(r.text)

# this function is called when the camera btn is pushed in index.html 
def mathocr(image):
  image_url = "data:image/jpg;base64," + base64.b64encode(image).decode()
  r = latex({
      'src': image_url, #image_uri('front/'+image_url),
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
  # for debug
  # print(r) 
  #the formula recognized
  if r['detection_map']['is_not_math'] == 0:
    result = r['latex_styled']

  #the formula not recognized
  else:
    result = "the formula was not recognized" #for debug

  return result