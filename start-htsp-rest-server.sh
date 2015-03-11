#!/bin/bash
PID=`ps aux | grep htsp_rest.py | grep -v grep | awk '{print $2}'`
if [ -z "$PID" ]; then
  PWD=`pwd`
  HOME=`dirname $0`
  cd $HOME
  nohup python htsp_rest_server.py >/dev/null 2>&1 &
  cd $PWD
else
  echo "already running: $PID"
fi
