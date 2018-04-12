#!/bin/bash

cd /git/FriendorFoe

git pull

pip3 install -r ./requirements.txt

cd ./Client/

echo '*****************************************'
echo '********** Autostarting Client **********'
echo '*****************************************'

python3.6 client.py