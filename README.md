Python 3.10.4

conda activate researchdt

pip install -r requirements.txt

python manage.py makemigrations
python manage.py makemigrations user
python manage.py migrate

python manage.py createsuperuser --email admin@example.com

python manage.py runserver

pip freeze > requirements.txt

python manage.py startapp 
