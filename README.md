**Codex Gigas** malware DNA profiling search engine discovers malware patterns and characteristics assisting individuals who are attracted in malware hunting.

![img](doc/47-preview.png?raw=true) 

# Codex Gigas
Codex Gigas is a malware profiling search engine that allows malware hunters and analysts to truly interrogate the internals of malware and perform searches over a large number of file characteristics. For instance, instead of relying on file-level hashes, we can compute other features such as imported functions, strings, constants, file segments, code regions, or anything that is defined in the file type specification, and that provides us with more than 142 possible searchable patterns, that can be combined.

Read the [user guide](doc/user-guide.md) to learn how it works.

##Contents
* [Configuration (optional)](#configuration-optional)
    * [MongoDB path](#mongodb-path)
    * [VirusTotal](#virustotal)
* [Ready-to-use virtual machines](#ready-to-use-virtual-machines)
* [Manually build Codex Gigas](#manually-build-codex-gigas)
* [Load Files](#load-files)
* [APT-notes samples](#apt-notes-samples)
* [Development](#development)
* [Codex Gigas Thanks](#codex-gigas-thanks)


## Configuration (optional)
### MongoDB path
The default path of the Mongo database is the parent folder of ```codex-backend``` and ```codex-frontend```. If you want to change that edit line 4 of ```docker-compose.yml```:
```
    - ../mongo-data/:/data/db
```

### VirusTotal
VirusTotal is used for retrieving antivirus results at request for a file. You can add your own [VirusTotal API key](https://www.virustotal.com/es-ar/documentation/public-api/) in ```src/secrets.py```. Then you should restart the container:
```
sudo docker-compose up
```

## Ready-to-use virtual machines
You can download your preferred vm file. Inside you'll find Codex Gigas running at startup on ```http://127.0.0.1:6100```.
* [VMware](https://www.dropbox.com/s/9qn13x9d8eegpgr/codex_vmware.zip?dl=0) (sha1: 9C6B3F8F37C8BD119E5C8A07050CB28C1A7E2DF3)
* [VirtualBox](https://www.dropbox.com/s/a6hxhkjpa8a3ek0/codex_vtbox.ova?dl=0) (sha1: 8289A8BEAF2D75A6D2B4E80ADEB943A806E26373)

VMs password: codex

## Manually build Codex Gigas 
If you don't want to use a Virtual Machine, you can manually install Codex Gigas on your system.
First install [docker](https://www.docker.com) and [docker-compose](https://docs.docker.com/compose/), then:
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
If everything goes well, Codex Gigas should be up and running on ```http://127.0.0.1:6100```. 

## Load files
To load files on a mass scale, drop them to ```files_to_load``` folder and execute the following command:
```
curl http://127.0.0.1:4500/api/v1/load_to_mongo
```



## APT-notes samples [https://github.com/kbandla/APTnotes] (https://github.com/kbandla/APTnotes)
We have gathered 5437 [executable samples](https://www.dropbox.com/s/zhv2du99ehlmm24/APTnotes-Samples.zip?dl=0) (sha1: 6EA9BBFBB5FB0EB0D025221A522D907E6D4956A0)
mentioned in APT reports over the last years. Ask for the zip password sending a DM to [CodexGigasSys twitter](https://twitter.com/codexgigassys)

## Development
Wanna contribute? Codex Gigas is an open, BSD-licensed, collaborative development effort that heavily relies on contributions from the whole community. We welcome tickets, pull requests, feature suggestions and bug fixing.

When developing new modules or patches, please try to comply to the general code style that we try to maintain across the project. When introducing new features or fixing significant bugs, please also include a summary and possibly also introduce comprehensive documentation in our guide.
If you want to debug the app it will be easier starting it as:
```
sudo docker-compose run --service-ports --rm api
```
This way the app does not run in the background and you can use ```embed()``` from [IPython](https://en.wikipedia.org/wiki/IPython)

Codex Gigas extracts the file metadata via plugins. Each plugin receives a file and returns a python dictionary that is saved in MongoDB. Plugins are located in ```src/PlugIns```. To add a new plugin for Windows executables create a file in ```src/PlugIns/PE/``` and add the plugin name in ```Prosessors/PEProcessor.py``` and ```PlugIns/PE/__init__.py```. 

## Codex Gigas Thanks
We would like to thanks the authors of the following tools, coming from other projects:

#### Projects
* yarGen (Florian Roth)            https://github.com/Neo23x0/yarGen
* pefile (Ero Carrera)             https://github.com/erocarrera/pefile
* ssdeep (jollheef)                https://github.com/jollheef/ssdeep
