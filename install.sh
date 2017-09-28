#!/bin/bash
echo "START"
apt-get update

apt-get install -y python-software-properties software-properties-common postgresql-9.6 postgresql-client-9.6 postgresql-contrib-9.6 postgresql-server-dev-9.6
/etc/init.d/postgresql start
apt-get install -y sudo
sudo -u postgres createdb hasker
sudo -u postgres psql --command "ALTER USER postgres WITH superuser password 'postgres';"

apt-get install -y nginx
#/etc/init.d/nginx start

apt-get install -y python
apt-get install -y python-pip
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install uwsgi
pip install -r requirements/test.txt
python manage.py test hasker.tests -p=*.py --settings=config.settings.test
python manage.py migrate
python manage.py runserver 0.0.0.0:80 --settings=config.settings.local
echo "END"

