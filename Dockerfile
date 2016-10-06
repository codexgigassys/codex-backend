FROM python:2.7
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
#ToDo: fix secrets.py add with an if
ADD yara/yara.zip* /tmp/
ADD yara/pestudio.zip* /tmp/
RUN apt-get clean && apt-get -o Debug::pkgProblemResolver=true -o Debug::Acquire::http=true update -qq && apt-get -o Debug::pkgProblemResolver=true -o Debug::Acquire::http=true install -y build-essential \
libpq-dev \
python-hachoir-metadata \
p7zip-full \
libffi-dev \
libssl-dev \
python-dev \
libfuzzy-dev \
python-numpy \
python-scipy \
python-matplotlib \
python-gevent \
python-pip \
python-magic \
python-crypto \
zip \
python-dateutil \
python-mysqldb \
redis-server \
autoconf \
openssl \
file \
python \
git \
autoconf \
automake \
libc-dev \
libtool \
python-dev \
unzip \
libfreetype6-dev \
libtaoframework-freetype-cil-dev \
libxft-dev && \
bash -c "wget -nc https://github.com/plusvic/yara/archive/v3.4.0.zip -O /tmp/yara.zip; echo a"  && \
unzip /tmp/yara.zip -d /tmp && \
pip install -r /myapp/src/pip_requirements.txt   && \
pip install -r /myapp/src/pip_yargen_requirements.txt && \
pip install -r /myapp/src/pip_vt_api_requirements.txt && \
cd /tmp/yara-3.4.0/ && ./bootstrap.sh && ./configure && \
cd /tmp/yara-3.4.0/ &&  make && make install && \
cd /myapp/yara && \
python /myapp/yara/binarly-sdk/setup.py install && \
cd /myapp/yara/yarGen-master && \
7z x -y good-strings.db.zip.001 -o/myapp/yara/yarGen-master && \
7z x -y good-opcodes.db.zip.001 -o/myapp/yara/yarGen-master && \
bash -c "wget -nc https://winitor.com/tools/pestudio/current/pestudio.zip -O /tmp/pestudio.zip; echo a" && \
unzip /tmp/pestudio.zip -d /tmp && \
cp /tmp/pestudio/xml/strings.xml /myapp/yara/yarGen-master/
#yargen
#RUN chmod +x /myapp/yara/setupYarGen.sh && sleep 1  && cat /myapp/yara/setupYarGen.sh
#RUN ["/myapp/yara/setupYarGen.sh"]
#ADD yara/yarGen-master.zip* /tmp/
#RUN bash -c "wget -nc https://github.com/Neo23x0/yarGen/archive/master.zip -O /tmp/yarGen-master.zip; echo a"
#RUN unzip /tmp/yarGen-master.zip -d  /tmp
#RUN if [ $(ls /myapp/yara/yarGen-master/) ]; then echo "yarGen-master folder already exists"; else mv /tmp/yarGen-master/ /myapp/yara/; fi
# https://github.com/kennethreitz/requests/issues/3215
ENV REQUESTS_CA_BUNDLE "/usr/local/lib/python2.7/site-packages/certifi/weak.pem"
#RUN cd /myapp/yara && python ./

#CMD ["python","/myapp/src/api2.py"]
#CMD ["/bin/bash"]
