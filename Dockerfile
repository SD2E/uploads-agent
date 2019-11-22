FROM sd2e/python3:ubuntu17

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /opt
ADD proj /opt/proj
ADD config.yml /config.yml

WORKDIR /opt
HEALTHCHECK CMD celery inspect ping -A proj -d $RABBITMQ_WORKER_NAME@$HOSTNAME

ADD entry.sh /entry.sh
RUN chmod +x /entry.sh
CMD ["./entry.sh"]
