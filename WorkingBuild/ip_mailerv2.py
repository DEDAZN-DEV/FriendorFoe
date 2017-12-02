#!/usr/bin/env python
# modified from http://elinux.org/RPi_Email_IP_On_Boot_Debian
import datetime
import smtplib
import subprocess
import urllib2
from email.mime.text import MIMEText

import global_cfg as cfg


def sendIP(to):
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(cfg.GMAIL_USER, cfg.GMAIL_PASSWORD)
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
    msg['From'] = cfg.GMAIL_USER
    msg['To'] = to
    smtpserver.sendmail(cfg.GMAIL_USER, [to], msg.as_string())
    smtpserver.quit()
