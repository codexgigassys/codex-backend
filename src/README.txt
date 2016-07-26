# tips

Easy way to extract lots of metadata at once.
Given a hashes.txt (one hash per line)

cat hashes.txt | xargs -I '{}' echo http://192.168.0.45:8081/api/v1/metadata?file_hash={} >> test.txt
wget -i test.txt
rename  's/metadata\?file_hash=//' *
-------
Workers:
rq worker checkup #start from malware checkup folder
rq worker default # start from virusTotal folder
------
Mount NFS filesystem on ubuntumal
sudo mount -t nfs ds-malware.lab:/volume1/samples /mnt/samples/
