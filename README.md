# Codex Gigas
CodexGigas is a malware profiling search engine that allows malware hunters and analysts to really interrogate the internals of malware and perform searches over a large number of file characteristics. For instance, instead of relying on file-level hashes, we can compute other features such as imported functions, strings, constants, file segments, code regions, or anything that is defined in the file type specification, and that provides us with more than 142 possible searchable patterns, that can be combined.

## Configuration (optional)
The default path of the Mongo database is the parent folder of ```codex-backend``` and ```codex-frontend```. If you want to change that edit line 4 of ```docker-compose.yml```:
```
    - ../mongo-data/:/data/db
```

## Install Codex

First install [docker](https://www.docker.com) and [docker-compose](https://docs.docker.com/compose/)
```
sudo apt-get install p7zip-full
git clone https://github.com/codexgigassys/codex-backend
git clone https://github.com/codexgigassys/codex-frontend
cd codex-backend/yara/
./setupYarGen.sh
cd ..
cp src/secrets.py.sample src/secrets.py
sudo docker-compose up
```
The next time you want to stop/start the containers:
```
sudo docker-compose stop
sudo docker-compose start
```

### VirusTotal
You can add your own [VirusTotal API key](https://www.virustotal.com/es-ar/documentation/public-api/) in ```src/secrets.py```. Then you should restart the container:
```
sudo docker-compose restart
```

### Load files
To load files on a mass scale, drop them to ```files_to_load``` folder and execute the following command:
```
curl http://127.0.0.1:4500/api/v1/load_to_mongo
```


### Development
Wanna contribute? CodexGigas is an open, BSD-licensed, collaborative development effort that heavily relies on contributions from the whole community. We welcome tickets, pull requests, feature suggestions.

When develping new modules or patches, please try to comply to the general code style that we try to maintain across the project. When introducing new features or fixing significant bugs, please also include some concise information and possibly also introduce comprehensive documentation in our guide.
If you want to debug the app it will be easier starting it as:
```
sudo docker-compose --service-ports --rm api
```
and in another terminal:
```
sudo docker-compose --serivce-ports --rm httpd
```
This way the app does not run in the background and you can use ```embed()``` from [IPython](https://en.wikipedia.org/wiki/IPython)

### Thanks to
[yarGen](https://github.com/Neo23x0/yarGen) by: Florian Roth

[pefile](https://github.com/erocarrera/pefile) by: Ero Carrera

[ssdeep](https://github.com/jollheef/ssdeep) by: jollheef

