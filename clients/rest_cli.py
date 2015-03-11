#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import math
import requests
import json
import datetime
import calendar
import urllib
import getopt
from unicode_utils import unicode_to_string

def strip_quotes(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s


def error_message(response):
    try:
        data = unicode_to_string(response.json())
        #print "data: " + str(data)
        return data['error']
    except ValueError:
        return response.reason

def show_error(response):
    print "error: " + str(error_message(response))

def print_usage():
    print 'Usage: ' + sys.argv[0] + " -y <year> -m <month> -d <day> -H <hour> -M <minute> -l <duration in minutes> -c <channel> -t <title> -u <user> -p <password> [--url=<url>] [--delete]"

def delete_dvr_record(url, channel, start_time, auth):
    unix_start_time = calendar.timegm(start_time.utctimetuple())
    entry_url = url + '/channel/' + str(urllib.quote(channel)) + '/start/' + str(unix_start_time)
    response = requests.delete(entry_url, auth=auth)
    if (response.ok):
        data = unicode_to_string(response.json())
        print "data: ", data
        return 0
    else:
        show_error(response)
        return 3

def utc_to_local(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= datetime.timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def add_timestamp(title, start_time):
    return title + " [rec=" + utc_to_local(start_time).strftime("%Y-%m-%d-%H-%M") + "]"

def clean_filename(name):
    name = name.decode("utf8")
    name = name.replace(": ", ", ").replace(":", ", ")
    name = name.replace(unicode("£ ", encoding="utf-8"), "GBP ")
    name = name.replace(unicode("£", encoding="utf-8"), "GBP ")
    return name

def add_dvr_record(url, channel, start_time, stop_time, title, auth, configName):
    unix_start_time = calendar.timegm(start_time.utctimetuple())
    unix_stop_time = calendar.timegm(stop_time.utctimetuple())
    name = clean_filename(add_timestamp(title, start_time))

    dvr_entry = {'channel': channel, 'start': unix_start_time, 'stop': unix_stop_time, 'title': name}
    if ('configName' != None):
        dvr_entry['configName'] = configName
    
#    print "auth: ", ' '.join(str(auth))

    response = requests.post(url, json.dumps(dvr_entry), auth=auth)
    if (response.ok):
        data = unicode_to_string(response.json())
        print "data: ", data
        return 0
    else:
        show_error(response)
        return 3

def main(argv):
    # {start_year-y {start_year} -m {start_month} -d {start_day} -H {start_hour} -M {start_minute} -l {length_minutes} -c "{isset(channel_name_external_quiet,channel_name)}" -t "{title}{testparam(episode,concat(" - ",episode))} [ch={channel_name}]" -u {device_username} -p {device_password} --configName tvbrowser --url=http://myrasp:9080
    inputfile = ''
    outputfile = ''
    year = None
    month = None
    day = None
    hour = None
    minute = None

    length = None

    channel = None
    title = None
    username = None
    password = None
    configName = None

    delete = False

    base_url = 'http://localhost:8080'
    try:
        opts, args = getopt.getopt(argv, "y:m:d:H:M:l:c:t:u:p:", ["delete", "url=", "configName="])
    except getopt.GetoptError:
        print_usage()
        return 2
    for opt, arg in opts:
        if opt == '--delete':
            delete = True
        elif opt == "-y":
            year = int(arg)
        elif opt == "-m":
            month = int(arg)
        elif opt == "-d":
            day = int(arg)
        elif opt == "-H":
            hour = int(arg)
        elif opt == "-M":
            minute = int(arg)
        elif opt == "-l":
            length = int(arg)
        elif opt == "-c":
            channel = strip_quotes(arg)
        elif opt == "-t":
            title = strip_quotes(arg)
        elif opt == "-u":
            username = strip_quotes(arg)
        elif opt == "-p":
            password = strip_quotes(arg)
        elif opt == "--url":
            base_url = strip_quotes(arg)
        elif opt == "--configName":
            configName = strip_quotes(arg)
        else:
            print "Unrecognised parameter: " + str(opt)
            print_usage()
            return 2
    if ((year == None) or (month == None) or (day == None) or (hour == None) or (minute == None) or (channel == None) or (username == None) or (password == None) or
        ((not delete) and ((length == None) or (title == None)))):
        print_usage()
        return 2
    start_time = datetime.datetime(year, month, day, hour, minute)
    unix_start_time = calendar.timegm(start_time.utctimetuple())
    #print "start_time: ", start_time, ", start_time.dst: ", start_time.dst()

    recordings_url = base_url + '/dvr/recordings'

    auth = (username, password)

    if (delete):
        return delete_dvr_record(recordings_url, channel, start_time, auth)
    else:
        stop_time = start_time + datetime.timedelta(minutes = length)
        return add_dvr_record(recordings_url, channel, start_time, stop_time, title, auth, configName)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
