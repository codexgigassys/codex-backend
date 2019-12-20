**Codex Gigas** malware DNA profiling search engine discovers malware patterns and characteristics assisting individuals who are attracted in malware hunting.

![img](doc/47-preview.png?raw=true) 

# Codex Gigas
Codex Gigas is a malware profiling search engine that allows malware hunters and analysts to truly interrogate the internals of malware and perform searches over a large number of file characteristics. For instance, instead of relying on file-level hashes, we can compute other features such as imported functions, strings, constants, file segments, code regions, or anything that is defined in the file type specification, and that provides us with more than 142 possible searchable patterns, that can be combined.

Read the [user guide](doc/user-guide.md) to learn how it works.

## Contents
* [Configuration (optional)](#configuration-optional)
    * [MongoDB path](#mongodb-path)
    * [VirusTotal](#virustotal)
* [Installation](#installation)
    * [Method 1: Download ready-to-use virtual machines](#method-1-download-ready-to-use-virtual-machines)
    * [Method 2: Installation without virtual machines](#method-2-installation-without-virtual-machines)
    * [Method 3: Manually build Codex Gigas Community Version](#method-3-manually-build-codex-gigas-community-version)
* [Load files](#load-files)
    * [Method 1: files_to_load folder](#method-1-files_to_load-folder)
    * [Method 2: via upload API](#method-2-via-upload-api)
    * [Method 3: via loadFile python script.](#method-3-via-loadfile-python-script)
* [APT-notes samples](#apt-notes-samples)
* [Logs](#logs)
* [Development](#development)
* [Codex Gigas Thanks](#codex-gigas-thanks)
* [License](#license)


## Configuration (optional)
### MongoDB path
The default path of the Mongo database is the parent folder of ```codex-backend```. If you want to change that edit the following line of ```pull-install.yml``` and ```docker-compose.yml``` before installation:
```
    - ../mongo-data/:/data/db
```

### VirusTotal
VirusTotal is used for retrieving antivirus results at request for a file or downloading new files. You can add one private API key, and one public API key. The private API key will only be used when required (downloading samples). Public API key will be used for downloading Antivirus scans. You can add your own [VirusTotal API keys](https://www.virustotal.com/es-ar/documentation/public-api/) in ```src/config/secrets.py```. Then you should restart the container:
```
sudo docker-compose up
```
## Installation
There are three ways to install CodexGigas Community version. We have ready-to-use Virtual Machines (easiest way). We also provide the docker pre-built images, so you can use CodexGigas without virtual machines. Lastly, you can manually build Codex Gigas docker images.
### Method 1: Download ready-to-use virtual machines
You can download your preferred vm file. Inside you'll find Codex Gigas running at startup on ```http://127.0.0.1:6100```.
* [VMware](https://www.dropbox.com/s/9qn13x9d8eegpgr/codex_vmware.zip?dl=0) (sha1: 9C6B3F8F37C8BD119E5C8A07050CB28C1A7E2DF3)
* [VirtualBox](https://www.dropbox.com/s/a6hxhkjpa8a3ek0/codex_vtbox.ova?dl=0) (sha1: 8289A8BEAF2D75A6D2B4E80ADEB943A806E26373)

VMs password: codex

### Method 2: Installation without virtual machines
First install [docker](https://www.docker.com) and [docker-compose](https://docs.docker.com/compose/), then:
```
mkdir codexgigas && cd codexgigas
git clone https://github.com/codexgigassys/codex-backend
cd codex-backend
sudo docker-compose -f pull-install.yml up
```
This will download the pre-built docker images (about 2GB) and start them up. 
The next time you want to stop/start the containers:
```
sudo docker-compose stop
sudo docker-compose start
```
### Method 3: Manually build Codex Gigas Community Version
If you don't want to use a Virtual Machine, you can manually install Codex Gigas on your system.
First install [docker](https://www.docker.com) and [docker-compose](https://docs.docker.com/compose/), then:
```
git clone https://github.com/codexgigassys/codex-backend
git clone https://github.com/codexgigassys/codex-frontend
cd codex-backend/
# if you want to use a DB on a different host, copy default_config and edit it (optional)
cp src/config/default_config.py src/config/secrets.py
sudo docker-compose up
```
The next time you want to stop/start the containers:
```
sudo docker-compose stop
sudo docker-compose start
```
If everything goes well, Codex Gigas should be up and running on ```http://127.0.0.1:6100```. 

## Load files
### Method 1: files_to_load folder
To load files on a mass scale, drop them to ```files_to_load``` folder and execute the following command:
```
curl http://127.0.0.1:4500/api/v1/load_to_mongo
```

### Method 2: via upload API
Is possible to upload a file via POST
```
curl -F file="@/home/user/somefile.exe" http://127.0.0.1:4500/api/v1/file/add
```

You can upload all the files under a folder with find+curl
```
find . -type f -exec curl -F file="@{}" http://127.0.0.1:4500/api/v1/file/add \;
```

### Method 3: via loadFile python script.





## APT-notes samples
We have gathered 5437 [executable samples](https://www.dropbox.com/s/zhv2du99ehlmm24/APTnotes-Samples.zip?dl=0) (sha1: 6EA9BBFBB5FB0EB0D025221A522D907E6D4956A0)
mentioned in APT reports over the last years. Ask for the zip password sending a DM to [CodexGigasSys twitter](https://twitter.com/codexgigassys). Source:  [https://github.com/aptnotes/data](https://github.com/aptnotes/data)

## Logs
From 2017-01-23, logging system has been moved from the default docker logging system, to a syslog container that uses rsyslog deamon. To view logs, cd to the codex-backend folder and execute:
```sudo docker-compose exec syslog tail -f /var/log/messages```
(change ```tail -f ``` for ```cat```, ```less``` or whatever suits your needs)

## Development
Wanna contribute? Codex Gigas Community is an open, BSD-licensed, collaborative development effort that heavily relies on contributions from the whole community. We welcome tickets, pull requests, feature suggestions and bug fixing.

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

## License
Copyright (c) 2016 Deloitte Argentina

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
