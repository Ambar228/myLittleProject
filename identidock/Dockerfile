FROM python:3.9

RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
RUN pip install \ 
	Flask==2.3.3 \ 
	uWSGI==2.0.21 \ 
	requests==2.31.0 \ 
	redis==4.6.0

WORKDIR /app
COPY app /app/
COPY cmd.sh /cmd.sh
RUN chmod +x /cmd.sh

EXPOSE 9090 9191
USER uwsgi

CMD ["/cmd.sh"]
