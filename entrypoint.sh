# migrate django
python /code/twels/manage.py makemigrations search
python /code/twels/manage.py migrate

python /code/twels/manage.py collectstatic --noinput
