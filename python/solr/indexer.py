import glob
from pathlib import Path
import traceback

import pysolr
from requests.auth import HTTPBasicAuth

from twels.utils.utils import print_in_red


if __name__ == '__main__':
    collection_name = "twels_collection"

    # TODO: use environment variables for credentials.
    username = 'Hisashi'
    password = 'Kojima'

    try:
        zookeeper = pysolr.ZooKeeper("zoo1:2181,zoo2:2181,zoo3:2181")
        solr = pysolr.SolrCloud(zookeeper, collection_name, auth=HTTPBasicAuth(username, password))

        PYTHON_ROOT_DIR = Path(__file__).resolve().parent.parent
        print('dir: ', PYTHON_ROOT_DIR)

        # TODO: すべてのページを登録するには時間がかかるので、今は一部だけを登録している。
        # html_paths = glob.glob(f'{PYTHON_ROOT_DIR}/web_crawler/web_pages/**/*.html', recursive=True)
        html_paths = glob.glob(f'{PYTHON_ROOT_DIR}/web_crawler/web_pages/manabitimes/*.html')
        print(f'{len(html_paths)} pages will be indexed.')

        docs = []
        for i in range(len(html_paths)):
            with open(html_paths[i]) as f:
                raw_doc: dict = solr.extract(f)

                doc = {
                    'id': str(i+1),
                    'title': raw_doc['file_metadata'][23],
                    'description': raw_doc['file_metadata'][21],
                    'url': raw_doc['file_metadata'][43],
                }
                docs.append(doc)
            solr.add(docs)
            print('document number: ', i)

        solr.commit()
        print('indexed!!')
    except pysolr.SolrError:
        print_in_red(traceback.format_exc())
