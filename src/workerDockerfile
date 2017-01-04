FROM python:2.7
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp/
ENV PYTHONUNBUFFERED=0
RUN apt-get clean && apt-get update && apt-get install -y build-essential \
libpq-dev \
libffi-dev \
libssl-dev \
python-dev \
libfuzzy-dev \
python-gevent \
python-pip \
python-magic \
python-crypto \
python-dateutil \
autoconf \
openssl \
file \
python \
autoconf \
automake \
libc-dev \
libtool && \
echo "Installing pip requirements" && \
pip install -r /myapp/pip_requirements.txt && \
pip install -r /myapp/pip_vt_api_requirements.txt
CMD ["/usr/local/bin/rq","worker", "-u", "redis://codexbackend_redis_1:6379/0", "task"]
