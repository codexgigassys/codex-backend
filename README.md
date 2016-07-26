# Codex Gigas
## Configuration (optional)
The default path of the Mongo database is the parent folder of ```codex-backend``` and ```codex-frontend```. If you want to change that edit line 4 of ```docker-compose.yml```:
```
    - ../mongo-data/:/data/db
```

## Install Codex

First install [docker](https://www.docker.com) and [docker-compose](https://docs.docker.com/compose/)
```
git clone https://github.com/codexgigas/codex-backend
git clone https://github.com/codexgigas/codex-frontend
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
To load files on a mass scale, drop them to ```files_to_load``` folder curl execute the following command:
```
curl http://127.0.0.1:4500/api/v1/load_to_mongo
```


### Development
If you want to debug the app it will be easier starting it as:
```
sudo docker-compose --service-ports --rm api
```
and in other terminal:
```
sudo docker-compose --serivce-ports --rm httpd
```
This way the app does not run in the background and you can use ```embed()``` from [IPython](https://en.wikipedia.org/wiki/IPython)

