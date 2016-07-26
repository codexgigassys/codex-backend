#!/bin/bash
if [ $(ls ./yarGen-master/ ) ]; then 
	echo "yarGen-master folder already exists"; 
 	exit 0
elif [ $(ls ./yarGen-master.zip ) ]; then
	unzip yarGen-master.zip 
else
        wget -nc https://github.com/Neo23x0/yarGen/archive/master.zip -O yarGen-master.zip
	unzip yarGen-master.zip 
fi
git clone --depth 1 https://github.com/binarlyhq/binarly-sdk/
#git clone https://github.com/Xen0ph0n/YaraGenerator/
