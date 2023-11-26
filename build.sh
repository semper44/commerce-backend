# install Dependencies
pip install -r requirements.txt

# run Migrations
python manage.py collectstatic --no-input
python manage.py migrate