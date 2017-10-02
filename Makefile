.PHONY: prod

define NGCONF
server {
    listen 80;
    server_name 0.0.0.0;
    charset utf-8;
    client_max_body_size 2M;

    location /media {
        alias /usr/local/hasker/media;
    }

    location /static {
        alias /usr/local/hasker/static;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:8000;
    }
}
endef
export NGCONF

prod:
	mkdir -p /usr/local/hasker/{media,static}
	apt-get update

	apt-get install -y postgresql-9.6 postgresql-contrib-9.6
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
	echo "$$NGCONF" > /etc/nginx/sites-enabled/hasker.conf
	/etc/init.d/nginx start

	uwsgi --socket 127.0.0.1:8000 --wsgi-file config/wsgi.py
