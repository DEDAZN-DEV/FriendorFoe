#!/bin/bash

sleep 5

echo '*****************************************'
echo '*********** Python Ver. Check ***********'
echo '*****************************************'

PKG_OK=$(dpkg-query -W --showformat='${Status}\n' python3.5|grep "install ok installed")
echo Checking for python3.5: $PKG_OK
if [ "" == "$PKG_OK" ]; then
  echo "Missing python3.5. Setting up python3.5 and pip."
  sudo apt-get update
  sudo apt-get --yes install python3.5 python3-pip
fi

sleep 5

echo '*****************************************'
echo '************ Git Repo Update ************'
echo '*****************************************'

cd /home/pi/git/FriendorFoe

git pull

sudo pip3 install -r ./requirements.txt

cd /home/pi/git/FriendorFoe/Client

echo '*****************************************'
echo '********** Autostarting Client **********'
echo '*****************************************'

python3.5 client.py &
