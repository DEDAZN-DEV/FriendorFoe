#!/usr/bin/env python
# modified from http://elinux.org/RPi_Email_IP_On_Boot_Debian
import datetime
import smtplib
import subprocess
import urllib2
from email.mime.text import MIMEText


def sendIP(to):
    gmail_user = 'stilwell.andrewk@gmail.com'
    gmail_password = 'whnqwmnpojxeqkyc'
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(gmail_user, gmail_password)
    today = datetime.date.today()
    # Very Linux Specific
    arg = 'ip route list'
    p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
    data = p.communicate()
    split_data = data[0].split()
    ipaddr = split_data[split_data.index('src') + 1]
    extipaddr = urllib2.urlopen("http://icanhazip.com").read()
    my_ip = 'Local address: %s\nExternal address: %s' % (ipaddr, extipaddr)
    msg = MIMEText(my_ip)
    msg['Subject'] = 'IP For RaspberryPi on %s' % today.strftime('%b %d %Y')
    msg['From'] = gmail_user
    msg['To'] = to
    smtpserver.sendmail(gmail_user, [to], msg.as_string())
    smtpserver.quit()
