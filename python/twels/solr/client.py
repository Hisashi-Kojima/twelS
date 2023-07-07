# -*- coding: utf-8 -*-
"""module description
"""
import pysolr
from requests.auth import HTTPBasicAuth


def get_solr_client() -> pysolr.SolrCloud:
    """ZooKeeperに問い合わせてSolrに接続する関数。"""
    # TODO: use environment variables for credentials.
    username = 'Hisashi'
    password = 'Kojima'

    collection_name = "twels_collection"

    zookeeper = pysolr.ZooKeeper("zoo1:2181,zoo2:2181,zoo3:2181")
    return pysolr.SolrCloud(zookeeper, collection_name, auth=HTTPBasicAuth(username, password))
