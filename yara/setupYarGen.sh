#!/bin/bash
if [ -d "./yarGen-master/" ]; then 
	echo "yarGen-master folder already exists"; 
 	exit 0
elif [ -f "./yarGen-master.zip" ]; then
	unzip yarGen-master.zip 
	7z x yarGen-master/good-opcodes.db.zip.001 -oyarGen-master
        7z x yarGen-master/good-strings.db.zip.001 -oyarGen-master
else
        wget -nc https://github.com/Neo23x0/yarGen/archive/master.zip -O yarGen-master.zip
	unzip yarGen-master.zip 
	7z x yarGen-master/good-opcodes.db.zip.001 -oyarGen-master
        7z x yarGen-master/good-strings.db.zip.001 -oyarGen-master
fi
git clone --depth 1 https://github.com/binarlyhq/binarly-sdk/
#git clone https://github.com/Xen0ph0n/YaraGenerator/
