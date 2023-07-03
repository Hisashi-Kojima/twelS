# migrate django
python /code/front/manage.py makemigrations
python /code/front/manage.py migrate

python /code/front/manage.py collectstatic --noinput

# create a Solr user.
curl --user solr:SolrRocks http://solr1:8983/api/cluster/security/authentication -H 'Content-type:application/json' -d '{"set-user": {"Hisashi":"Kojima"}}'
curl --user solr:SolrRocks http://solr1:8983/solr/admin/authorization -H 'Content-type:application/json' -d '{"set-user-role" : {"Hisashi": ["admin"]}}'
curl --user Hisashi:Kojima http://solr1:8983/api/cluster/security/authentication -H 'Content-type:application/json' -d '{"delete-user": ["solr"]}'
