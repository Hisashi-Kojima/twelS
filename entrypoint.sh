# migrate django
python /code/front/manage.py makemigrations search
python /code/front/manage.py migrate

python /code/front/manage.py collectstatic --noinput
