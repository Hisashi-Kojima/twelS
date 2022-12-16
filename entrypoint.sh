# migrate django
python /code/front/manage.py makemigrations
python /code/front/manage.py migrate

python /code/front/manage.py collectstatic --noinput
