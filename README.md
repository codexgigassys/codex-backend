CodexGigas malware DNA profiling search engine discovers malware patterns and characteristics assisting individuals who are attracted in malware hunting.

## Contents
  * [Codex Gigas](#codex-gigas)
    * [Configuration (optional)](#configuration-optional)
    * [Install Codex](#install-codex)
      * [VirusTotal](#virustotal)
      * [Load files](#load-files)
    * [User Guide](#user-guide)
      * [Searching with codex](#searching-with-codex)
        * [File buttons functionality](#file-buttons-functionality)
        * [Searching for Dino (part of Animal Farm) using strings:](#searching-for-dino-part-of-animal-farm-using-strings)
        * [Searching for Zeus by file section:](#searching-for-zeus-by-file-section)
        * [Advanced search with codex](#advanced-search-with-codex)
          * [Multiple search](#multiple-search)
      * [Samples handling](#samples-handling)
        * [Upload](#upload)
        * [Mass Download](#mass-download)
      * [Simple Compare Function](#simple-compare-function)
      * [Sample Upload](#sample-upload)
      * [Massive Load of Files](#massive-load-of-files)
      * [Sample Process with Codex-Gigas](#sample-process-with-codex-gigas)
      * [Massive Download with Codex-Gigas](#massive-download-with-codex-gigas)
    * [Development](#development)
    * [Codex Thanks](#codex-thanks)
        * [Projects](#projects)

# Codex Gigas
CodexGigas is a malware profiling search engine that allows malware hunters and analysts to really interrogate the internals of malware and perform searches over a large number of file characteristics. For instance, instead of relying on file-level hashes, we can compute other features such as imported functions, strings, constants, file segments, code regions, or anything that is defined in the file type specification, and that provides us with more than 142 possible searchable patterns, that can be combined.

## Configuration (optional)
### MongoDB path
The default path of the Mongo database is the parent folder of ```codex-backend``` and ```codex-frontend```. If you want to change that edit line 4 of ```docker-compose.yml```:
```
    - ../mongo-data/:/data/db
```

### VirusTotal
VirusTotal is used for retrieving antivirus results at request for a file. You can add your own [VirusTotal API key](https://www.virustotal.com/es-ar/documentation/public-api/) in ```src/secrets.py```. Then you should restart the container:
```
sudo docker-compose restart
```


## Install Codex

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

### Load files
To load files on a mass scale, drop them to ```files_to_load``` folder and execute the following command:
```
curl http://127.0.0.1:4500/api/v1/load_to_mongo
```

## User Guide
After starting the docker containers, Codex web app will be available on ```http://127.0.0.1:6100```.

### Searching with codex
We will search for Stuxnet, Dino and Zeus in order to demonstrate some of the engine capabilities:
**Searching for Stuxnet by DLL**
Malware samples may make use of specific libraries and DLLs in order to run. As an example, Stuxnet uses ‘s7otbxdx.dll’, which is a .dll that’s part of the Siemens Simatic S7 PLC (an automation system based on Programmable Logic Computers). 
With this information we proceed to launch our search by Library. 

![img](doc/02-search_tree.png?raw=true)
 
The following box will appear:

![img](doc/03-searchbox.png?raw=true)

 
We type the library of our interest, select the limit of results that we want and click on the search button. If you use 0 as limit, it will do a limitless search, so, be careful using this.
Note that if you type a .dll with a typo or if the .dll is not present in the database, it will highlight the textbox in red, as shown below:

![img](doc/04-library_textbox.png?raw=true)

 
Also, we can select the attributes of our interest by selecting one or multiple categories of the “Attributes for results preview” dropdown list. For this example we will use Time Date Stamp, Description and Size. If you don’t select any attribute, it will show sha1, description and size of each file that matches the search criteria.
The results will look like the image below:

![img](doc/05-search-dll.png?raw=true)
 
You can use the **filter function** to search for a particular attribute among the ones you’ve selected for the search, i.e: Filtering by size or TimeDateStamp:

![img](doc/06-results-filter.png?raw=true)

![img](doc/07-results-filter2.png?raw=true) 

As you can see, there are multiple buttons that can be useful to find more data.  

![img](doc/08-buttons.png?raw=true)

If we select the checkbutton “**Check all**”, it will select all results found, including the ones not present in the current page.

![img](doc/09-buttons2.png?raw=true)
 
The **download button** will download the checked results in a .zip file. The file’s password is “codex”. **Use this utility at your own risk!**

![img](doc/10-buttons.png?raw=true)

The **export button** will download a text file with the metadata gathered from the selected files:

![img](doc/11-export-example.png?raw=true)

The **process button** will add the file to the process queue:

![img](doc/12-button-process.png?raw=true)

This can be useful to re-process files if you change or add a new plugin.
The **Copy hashes button** will copy all selected hashes.

![img](doc/13-button-copy-hashes.png?raw=true) 

The **Generate Yara Rule** button will create a Yara rule for the selected files. This uses [yarGen](https://github.com/Neo23x0/yarGen), so make sure you have at least 5GB of RAM on the machine you plan to use yarGen.

![img](doc/14-button-yara.png?raw=true)

In addition, you can select one of the results and explore its **metadata tree**:

![img](doc/15-file-json.png?raw=true)

The metadata tree is organized in several categories, and it will vary depending on the file.

#### File buttons functionality
The **Download button** has the same functionality of the above button, but this will download only the file you’re currently viewing. The password for the .zip file is “codex”.

![img](doc/16-file-download.png?raw=true)
 
The **Process Button** will automatically re-process the file and update the results:

 ![img](doc/17-file-process.png?raw=true)

 The **Export Button** will export the metadata information to a .txt file:

![img](doc/18-file-export.png?raw=true) 

The **VT scan Data** button will gather the information found for the file hash you’re currently viewing, and add it to the metadata tree:

![img](doc/19-file-vt-scan.png?raw=true)

In the scan span, you’ll see further information about the results thrown by each Antivirus vendor:

![img](doc/20-file-scans.png?raw=true) 

#### Searching for Dino (part of Animal Farm) using strings:

The binary’s original name, “Dino.exe”, has been left visible by its authors. We can use this information to search for other Dino samples:

![img](doc/21-search-tree2.png?raw=true)
 
Type the desired string, “dino.exe” in this case:

![img](doc/22-search-dino.exe.png?raw=true)

Once you click on **search**, you will see the files that match the criteria:

![img](doc/23-results-dino.exe.png?raw=true)

#### Searching for Zeus by file section:

Common file sections may be observed across malware variants. In this case, the SHA-1 of the .data section for Zeus is ‘edbc64b30aceabd6e7d32defc698c1475861a42d’

![img](doc/24-search-tree-section-hash.png?raw=true)

![img](doc/25-results-search-by-section-hash.png?raw=true)
 
As you can see above, there are lots of files that matches the .data section with this hash. The Size and Time date stamp are the same for all the findings. You can visualize this easily by using the **Charts section** in the right of the screen:

![img](doc/26-charts.png?raw=true) 

You can click in the column’s name to **sort** the results by the column criteria, in this example we will click on file_entropy and see what happens:

![img](doc/27-results-sort.png?raw=true)

![img](doc/28-results-hash.png?raw=true) 

#### Advanced search with codex
##### Multiple search
Following the last example, suppose that we want all the files that match with other additional criteria, such as section name. We can select this criteria on the search box and add it to the current search:

![img](doc/29-tree-menu-section-name.png?raw=true)
 
An additional box will show:

![img](doc/30-searchbox-section-hash.png?raw=true)

You can add all the criteria you want:

![img](doc/31-searchbox-section-hash2.png?raw=true)



You can erase one of the selected criteria by clicking on the X in the right side of the text box.
Also, some criteria will show a plus sign in the right side, this means that you can add more criteria of the same type:


![img](doc/32-searchbox-section-hash3.png?raw=true)

![img](doc/33-searchbox-section-hash4.png?raw=true)

### Samples handling
#### Upload


#### Mass Download
You can simply download samples by pasting a list of hashes into the textbox. You will get a zip file with “codex” as password. 

![img](doc/01-download.png?raw=true)


 
### Simple Compare Function
Another useful feature of CodexGigas is the Simple Compare function. This can be found on the right side of the screen, once we’ve already done a search:

![img](doc/34-simple-compare.png?raw=true)


This will compare two files of your best choice and will provide a way to visualize the similarities and differences of both files. Just select the files you need and drag them to one of the blocks shown. You can click on **maximize** to fit the screen and have a better visualization of the results:

![img](doc/35-simple-compare2.png?raw=true)

Above you will see the metadata of each individual file, and below the comparison of both:

![img](doc/36-simple-compare3.png?raw=true)

In the **Diff tab** you can see:
•	Modified attributes, highlighted in yellow.
•	New attributes, highlighted in green.
•	Deleted attributes, highlighted in red.
•	Equal attributes will be shown in white.


![img](doc/37-simple-compare4.png?raw=true) 

![img](doc/38-simple-compare5.png?raw=true)


These comparisons are made using the file in the first box as base.


In the equal tab, you will see all metadata that match both files:

![img](doc/39-equals.png?raw=true)

### Sample Upload

Among the multiple features that Codex-Gigas has, it provides the capability to upload a sample of our choice, and process it to gather more information about the file’s metadata.
To do this, go to the Upload tab in the features panel. You will see the following page:

![img](doc/40-menu-upload.png?raw=true)


To upload a file, click on the Browse button, navigate and check the file to upload. 

![img](doc/41-upload-example.png?raw=true)
 
Once uploaded, it’ll show the SHA-1 hash for the file. Take note of this hash, since you’ll need it to get the information gathered by Codex-Gigas engine.

### Massive Load of Files

In order to upload more than one file at the time, go to the Load tab in the features panel. The following screen will show:


![img](doc/42-load-example.png?raw=true) 

Click on load and choose all the desired files.

![img](doc/43-load-example2.png?raw=true)

![img](doc/44-load-example3.png?raw=true) 
 
### Sample Process with Codex-Gigas

You are able to get the metadata information of each of the files you’ve uploaded searching by the file hash (MD5, SHA-1, SHA-256) or any other attributes you already know of the files. 
To do this, go to the Process tab in the features panel and copy the hashes of the files you want the information from, and click on Process:

![img](doc/45-process-example.png?raw=true)

If some of the hashes are not in Codex-Gigas, the legend “Not Found” will be shown, listing the missing file’s hashes.
Once you’ve processed the desired fields, you can search for them with the Search functionality.

### Massive Download with Codex-Gigas

Codex-gigas let you download all existing files in the Codex’ database. 
To do this, go to the download tab in the features panel, copy the file(s) hash(es) you want to download, and click on the Download button. It will download a .zip file with the files present in the database. Once again, the password of the .zip file is “codex”.

![img](doc/46-process-example2.png?raw=true)
 


## Development
Wanna contribute? CodexGigas is an open, BSD-licensed, collaborative development effort that heavily relies on contributions from the whole community. We welcome tickets, pull requests, feature suggestions.

When develping new modules or patches, please try to comply to the general code style that we try to maintain across the project. When introducing new features or fixing significant bugs, please also include some concise information and possibly also introduce comprehensive documentation in our guide.
If you want to debug the app it will be easier starting it as:
```
sudo docker-compose --service-ports --rm api
```
This way the app does not run in the background and you can use ```embed()``` from [IPython](https://en.wikipedia.org/wiki/IPython)

Codex extracts the file metadata via plugins. Each plugin recieves a file and returns a python dictionary that is saved in MongoDB. Plugins are located in ```src/PlugIns```. To add a new Plugin for Windows executables create a file in ```src/PlugIns/PE/``` and add the plugin name in ```Prosessors/PEProcessor.py``` and ```PlugIns/PE/__init__.py```. 

## Codex Thanks
We would like to thanks the authors of these tools, coming from other projects:

#### Projects
* yarGen (Florian Roth)            https://github.com/Neo23x0/yarGen
* pefile (Ero Carrera)             https://github.com/erocarrera/pefile
* ssdeep (jollheef)                https://github.com/jollheef/ssdeep
