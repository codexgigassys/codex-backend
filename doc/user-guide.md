# Contents
 * [User Guide](#user-guide)
   * [Searching with Codex Gigas](#searching-with-codex-gigas)
     * [Advanced search with Codex Gigas](#advanced-search-with-codex-gigas)
     * [Searching for Stuxnet by DLL](#searching-for-stuxnet-by-dll)
     * [Searching for Dino (part of Animal Farm APT) using strings](#searching-for-dino-part-of-animal-farm-apt-using-strings)
     * [Searching for Zeus by file section](#searching-for-zeus-by-file-section)
     * [Simple Compare Function](#simple-compare-function)
    * [Samples handling](#samples-handling)
     * [File buttons functionality](#file-buttons-functionality)
     * [Sample Download](#sample-download)
     * [Sample Upload](#sample-upload)
     * [Massive sample Upload](#massive-sample-upload)
     * [Sample Process with Codex Gigas](#sample-process-with-codex-gigas)

# User Guide
After starting the docker containers, Codex Gigas web app will be available on ```http://127.0.0.1:6100```.

## Searching with Codex Gigas

### Advanced search with Codex Gigas
If we want all the files that match with other criteria such as section name, we can select this criteria on the search box and add it to the current search:

![img](29-tree-menu-section-name.png?raw=true)
 
An additional box will show:

![img](30-searchbox-section-hash.png?raw=true)

You can add all the criteria you want:

![img](31-searchbox-section-hash2.png?raw=true)

You can erase one of the selected criteria by clicking on the X in the right side of the text box.
Also, some criteria will show a plus sign in the right side, this means that you can add more criteria of the same type:

![img](32-searchbox-section-hash3.png?raw=true)

![img](33-searchbox-section-hash4.png?raw=true)

We will search for Stuxnet, Dino and Zeus in order to demonstrate some of the engine capabilities.


### Searching for Stuxnet by DLL:
Malware samples may make use of specific libraries and DLLs in order to run. As an example, Stuxnet uses ‘s7otbxdx.dll’, which is a .dll that’s part of the Siemens Simatic S7 PLC (an automation system based on Programmable Logic Computers). 
With this information we proceed to launch our search by Library. 

![img](02-search_tree.png?raw=true)
 
The following box will appear:

![img](03-searchbox.png?raw=true)

 We type the ‘s7otbxdx.dll’ library in the box, select the limit of results that we want and click on the search button. If you use 0 as limit, it will do a limitless search, so be careful when using this option.
Note that if you type a .dll with a typo or if the .dll is not present in the database, it will highlight the textbox in red, as shown below:

![img](04-library_textbox.png?raw=true)

Also, we can select the attributes of our interest by selecting one or multiple categories of the “Attributes for results preview” dropdown list. For this example we will use Time Date Stamp, Description and Size. If you don’t select any attribute, it will show SHA1, description and size of each file that matches the search criteria.
The results will look like the image below:

![img](05-search-dll.png?raw=true)
 
You can use the **filter function** to search for a particular attribute among the ones you’ve selected for the search, i.e: Filtering by size or TimeDateStamp:

![img](06-results-filter.png?raw=true)

![img](07-results-filter2.png?raw=true) 

As you can see, there are multiple buttons that can be useful to find more data.  

![img](08-buttons.png?raw=true)

If we select the check button “**Check all**”, it will select all results found, including the ones not present in the current page.

![img](09-buttons2.png?raw=true)
 
The **download button** will download the checked results in a .zip file. The file’s password is “codex”. 

![img](10-buttons.png?raw=true)

The **export button** will download a text file containing the metadata gathered from the selected files:

![img](11-export-example.png?raw=true)

The **process button** will add the file to the process queue:

![img](12-button-process.png?raw=true)

This can be useful to re-process files if you change or add a new plugin.
The **Copy hashes button** will copy all selected hashes.

![img](13-button-copy-hashes.png?raw=true) 

The **Generate Yara Rule** button will create a Yara rule for the selected files. This uses [yarGen](https://github.com/Neo23x0/yarGen), so make sure you have at least 5GB of RAM on the machine you plan to use yarGen.

![img](14-button-yara.png?raw=true)

In addition, you can select one of the results and explore its **metadata tree**:

![img](15-file-json.png?raw=true)

The metadata tree is organized in several categories, and it will vary depending on the file.


### Searching for Dino (part of Animal Farm APT) using strings:

The binary’s original name, “Dino.exe”, has been left visible by its authors. We can use this information to search for other Dino samples:

![img](21-search-tree2.png?raw=true)
 
Type the desired string, “dino.exe” in this case:

![img](22-search-dino.exe.png?raw=true)

Once you click on **search**, you will see the files that match the criteria:

![img](23-results-dino.exe.png?raw=true)


### Searching for Zeus by file section:

Common file sections may be observed across malware variants. In this case, the SHA1 of the .data section for Zeus is ‘edbc64b30aceabd6e7d32defc698c1475861a42d’

![img](24-search-tree-section-hash.png?raw=true)

![img](25-results-search-by-section-hash.png?raw=true)
 
As you can see above, there are lots of files that matches the .data section with this hash. The Size and Time date stamp are the same for all the findings. You can visualize this easily by using the **Charts section** in the right of the screen:

![img](26-charts.png?raw=true) 

You can click in the column’s name to **sort** the results by the column criteria, in this example we will click on file_entropy and see what happens:

![img](27-results-sort.png?raw=true)

![img](28-results-hash.png?raw=true) 


### Simple Compare Function
Another useful feature of Codex Gigas is the Simple Compare function. This can be found on the right side of the screen, once we’ve already done a search:

![img](34-simple-compare.png?raw=true)

This will compare two files of your best choice and will provide a way to visualize the similarities and differences between both files. Just select the files you need and drag them to one of the blocks shown. You can click on **maximize** to fit the screen and have a better visualization of the results:

![img](35-simple-compare2.png?raw=true)

Above you will see the metadata of each individual file, and below the comparison of both:

![img](36-simple-compare3.png?raw=true)

In the **Diff tab** you can see:
•	Modified attributes, highlighted in yellow.
•	New attributes, highlighted in green.
•	Deleted attributes, highlighted in red.
•	Equal attributes will be shown in white.

![img](37-simple-compare4.png?raw=true) 

![img](38-simple-compare5.png?raw=true)

These comparisons are made using the file in the first box as base.

In the equal tab, you will see all metadata that match both files:

![img](39-equals.png?raw=true)


## Samples handling

### File buttons functionality
The **Download button** has almost the same functionality as the download button mentioned before, but this will download only the file you’re currently viewing. The password for the .zip file is “codex”. 

![img](16-file-download.png?raw=true)
 
The **Process Button** will automatically re-process the file and update the results:

![img](17-file-process.png?raw=true)

The **Export Button** will export the metadata information to a .txt file:

![img](18-file-export.png?raw=true) 

The **VT scan Data** button will gather the information found for the file hash you’re currently viewing, and add it to the metadata tree:

![img](19-file-vt-scan.png?raw=true)

In the scan span, you’ll see further information about the results thrown by each Antivirus vendor:

![img](20-file-scans.png?raw=true) 


### Sample Download
You can download multiple samples by pasting a list of hashes into the textbox of the download tab. You will get a zip file with “codex” as password. **Use this functionality at your own risk!**

![img](46-process-example2.png?raw=true)

You can also download a file by using the download button described in the "File buttons functionality" section.


### Sample Upload

Among the multiple features that Codex Gigas has, it provides the capability to upload a sample of our choice, and process it to gather more information about the file’s metadata.
To do this, go to the Upload tab in the features panel. You will see the following page:

![img](40-menu-upload.png?raw=true)

To upload a file, click on the Browse button, navigate and check the file to upload. 

![img](41-upload-example.png?raw=true)
 
Once uploaded, it’ll show the SHA1 hash for the file. Take note of this hash, since you’ll need it to get the information gathered by Codex Gigas engine.


### Massive sample Upload

In order to upload more than one file at the time, go to the Load tab in the features panel. The following screen will show:

![img](42-load-example.png?raw=true) 

Click on load and choose all the desired files.

![img](43-load-example2.png?raw=true)

![img](44-load-example3.png?raw=true) 


### Sample Process with Codex Gigas

You are able to get the metadata information of each of the files you’ve uploaded searching by the file hash (MD5, SHA1, SHA256) or any other attributes you already know of the files. 
To do this, go to the Process tab in the features panel and copy the hashes of the files you want the information from, and click on Process:

![img](45-process-example.png?raw=true)

If some of the hashes are not found in Codex Gigas, the legend “Not Found” will be shown, and the missing file’s hashes will be listed.
Once you’ve processed the desired fields, you can search for them with the Search functionality.
