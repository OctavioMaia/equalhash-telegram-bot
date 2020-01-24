FROM python:alpine
MAINTAINER Octávio Maia

RUN set -eux \
  && pip install pymongo \
  && pip install urllib3 \
  && pip install pytelegrambotapi

RUN mkdir /opt/equalhash
COPY equalhash /opt/equalhash
RUN chmod -R 644 /opt/equalhash

RUN echo "*    *    *    *    *    python3 /opt/equalhash/checkWorkers.py" >> /etc/crontabs/root

WORKDIR /opt/equalhash

ENTRYPOINT ["/bin/sh","/opt/equalhash/docker-entrypoint.sh"]

CMD ["python3","/opt/equalhash/bot-EqualHash.py"]