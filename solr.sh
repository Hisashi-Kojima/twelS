# initialize Solr collection.
curl --user Hisashi:Kojima "http://solr1:8983/solr/admin/collections?action=CREATE&name=twels_collection&numShards=2&replicationFactor=2&collection.configName=myconf"
python /code/solr/indexer.py
