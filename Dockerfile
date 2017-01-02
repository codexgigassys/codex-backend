FROM python:2.7
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
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
echo "Installing yarGen-master" && \
wget -nv -nc https://github.com/Neo23x0/yarGen/archive/master.zip -O /myapp/yara/yarGen-master.zip && \
cd /myapp/yara/ && \
unzip /myapp/yara/yarGen-master.zip -d /myapp/yara/ && \
7z x /myapp/yara/yarGen-master/good-opcodes.db.zip.001 -oyarGen-master && \
7z x /myapp/yara/yarGen-master/good-strings.db.zip.001 -oyarGen-master && \
git clone --depth 1 https://github.com/binarlyhq/binarly-sdk/ /myapp/yara/binarly-sdk && \
wget -nv -nc https://github.com/plusvic/yara/archive/v3.4.0.zip -O /tmp/yara.zip && \
unzip /tmp/yara.zip -d /tmp && \
echo "Installing pip requirements" && \
pip install -r /myapp/src/pip_requirements.txt   && \
pip install -r /myapp/src/pip_yargen_requirements.txt && \
pip install -r /myapp/src/pip_vt_api_requirements.txt && \
cd /tmp/yara-3.4.0/ && ./bootstrap.sh && ./configure && \
cd /tmp/yara-3.4.0/ &&  make && make install && \
cd /myapp/yara && \
python /myapp/yara/binarly-sdk/setup.py install && \
cd /myapp/yara/yarGen-master && \
7z x -y /myapp/yara/yarGen-master/good-strings.db.zip.001 -o/myapp/yara/yarGen-master && \
7z x -y /myapp/yara/yarGen-master/good-opcodes.db.zip.001 -o/myapp/yara/yarGen-master && \
wget -nv -nc https://winitor.com/tools/pestudio/current/pestudio.zip -O /tmp/pestudio.zip  && \
unzip /tmp/pestudio.zip -d /tmp && \
cp /tmp/xml/strings.xml /myapp/yara/yarGen-master/ && \
rm -rf /tmp/yara-3.4.0/ && \
rm -f /tmp/pestudio.zip && \
rm -f /tmp/yara.zip && \
rm -rf /tmp/pestudio/ && \
rm -f /myapp/yara/yarGen-master.zip && \
rm -f /myapp/yara/yarGen-master/good-opcodes.db.zip.001 && \
rm -f /myapp/yara/yarGen-master/good-opcodes.db.zip.002 && \
rm -f /myapp/yara/yarGen-master/good-opcodes.db.zip.003 && \
rm -f /myapp/yara/yarGen-master/good-opcodes.db.zip.004 && \
rm -f /myapp/yara/yarGen-master/good-opcodes.db.zip.005 && \
rm -f /myapp/yara/yarGen-master/good-opcodes.db.zip.006 && \
rm -f /myapp/yara/yarGen-master/good-strings.db.zip.001 && \
rm -f /myapp/yara/yarGen-master/good-strings.db.zip.002 && \
rm -f /myapp/yara/yarGen-master/good-strings.db.zip.003 && \
rm -f /myapp/yara/yarGen-master/good-strings.db.zip.004

#CMD ["python","/myapp/src/api2.py"]
