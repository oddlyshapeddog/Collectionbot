FROM python:3.7-alpine

RUN apk update && \
  apk add gcc linux-headers

COPY . /app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
WORKDIR /app
RUN mkdir -p /var/log/supervisord
RUN pip install -r requirements.txt

# CMD ["/usr/bin/supervisord"]
CMD ["echo a"]
