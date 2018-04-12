#!/bin/bash

echo '*****************************************'
echo '*********** Python Ver. Check ***********'
echo '*****************************************'

PKG_OK=$(dpkg-query -W --showformat='${Status}\n' python3.6|grep "install ok installed")
echo Checking for python3.5: $PKG_OK
if [ "" == "$PKG_OK" ]; then
  echo "Missing python3.5. Setting up python3.5 and pip."
  sudo apt-get update
  sudo apt-get --yes install python3.5 python3-pip
fi

echo '*****************************************'
echo '************ Git Repo Update ************'
echo '*****************************************'

cd /git/FriendorFoe

git pull

pip3 install -r ./requirements.txt

cd ./Client/

echo '*****************************************'
echo '********** Autostarting Client **********'
echo '*****************************************'

python3.5 client.py
