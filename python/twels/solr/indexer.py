# -*- coding: utf-8 -*-
"""initialize Solr.
"""
import glob
from pathlib import Path
import traceback

import pysolr

from twels.snippet.snippet import Snippet
from twels.solr.client import get_solr_client
from twels.utils.utils import print_in_red


if __name__ == '__main__':
    try:
        PYTHON_ROOT_DIR = Path(__file__).resolve().parent.parent.parent

        # TODO: すべてのページを登録するには時間がかかるので、今は一部だけを登録している。
        # html_paths = glob.glob(f'{PYTHON_ROOT_DIR}/web_crawler/web_pages/**/*.html', recursive=True)
        html_paths = glob.glob(f'{PYTHON_ROOT_DIR}/web_crawler/web_pages/manabitimes/*.html')
        print(f'{len(html_paths)} pages will be indexed.')

        solr = get_solr_client()

        docs = []
        for i in range(len(html_paths)):
            with open(html_paths[i]) as f:
                raw_doc: dict = solr.extract(f)
                html_content = raw_doc['file'].replace('<?xml version="1.0" encoding="UTF-8"?>', '')

                doc = {
                    'id': str(i+1),
                    'title': raw_doc['file_metadata'][23],
                    'description': raw_doc['file_metadata'][21],
                    'url': raw_doc['file_metadata'][43],
                    'content': Snippet(html_content).text
                }
                docs.append(doc)
            print('document number: ', i+1)
        solr.add(docs)

        solr.commit()
        print('indexed!!')
    except pysolr.SolrError:
        print_in_red(traceback.format_exc())
