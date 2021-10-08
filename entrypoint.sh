# migrate django
python /code/twelS/manage.py makemigrations search
python /code/twelS/manage.py migrate

python /code/twelS/manage.py collectstatic --noinput
