#!/bin/bash
echo "START"
apt-get update

apt-get install -y python-software-properties software-properties-common postgresql-9.6 postgresql-client-9.6 postgresql-contrib-9.6
/etc/init.d/postgresql start
su postgres
createdb hasker
psql --command "ALTER USER postgres WITH superuser password 'postgres';"
exit

apt-get install nginx

apt-get install git
git clone https://github.com/alega19/hasker
cd hasker/
apt-get install python (Y/n)
apt-get install python-pip
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install uwsgi
pip install -r requirements/production.txt
echo "END"

