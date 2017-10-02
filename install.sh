#!/bin/bash
echo "START"
NGCONF="server {\n
    listen 80;\n
    server_name 0.0.0.0;\n
    charset utf-8;\n
    client_max_body_size 2M;\n
\n
    location /media {\n
        alias /usr/local/hasker/media;\n
    }\n
\n
    location /static {\n
        alias /usr/local/hasker/static;\n
    }\n
\n
    location / {\n
        include uwsgi_params;\n
        uwsgi_pass 127.0.0.1:8000;\n
    }\n
}\n"
mkdir -p /usr/local/hasker/{media,static};

apt-get update

apt-get install -y python-software-properties software-properties-common postgresql-9.6 postgresql-client-9.6 postgresql-contrib-9.6 postgresql-server-dev-9.6
/etc/init.d/postgresql start
apt-get install -y sudo
sudo -u postgres createdb hasker
sudo -u postgres psql --command "ALTER USER postgres WITH superuser password 'postgres';"

apt-get install -y python
apt-get install -y python-pip
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install uwsgi
pip install -r requirements/production.txt
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py collectstatic

apt-get install -y nginx
rm /etc/nginx/sites-enabled/default
echo $NGCONF > /etc/nginx/sites-enabled/hasker.conf
/etc/init.d/nginx start

uwsgi --socket 127.0.0.1:8000 --wsgi-file config/wsgi.py 
echo "END"
