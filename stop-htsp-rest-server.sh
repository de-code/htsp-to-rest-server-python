#!/bin/bash
PID=`ps aux | grep htsp_rest_server.py | grep -v grep | awk '{print $2}'`
if [ -z "$PID" ]; then
  echo "No PIDs found"
else
  echo "Found PIDs: $PID"
  kill -9 $PID
fi
