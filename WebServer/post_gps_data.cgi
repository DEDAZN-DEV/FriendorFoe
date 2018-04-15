#!/usr/bin/python2.7
import cgi
import cgitb
import json


if __name__ == "__main__":
    print("Content-Type: text/plain\n")
    cgitb.enable()
    
    gps_data = cgi.FieldStorage()
    gps_data = json.loads(gps_data.value)
    gps_data["response"] = "Received gps data"

    response_string = json.dumps(gps_data)
    print(response_string) 

