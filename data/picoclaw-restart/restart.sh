#!/bin/sh

rm /root/.picoclaw/workspace/sessions/*
#rc-service picoclaw restart
#sh -c "sleep 1; rc-service picoclaw restart" &
#setsid rc-service picoclaw restart &
#kill -TERM $(cat /run/picoclaw.pid)
kill $(pgrep -P $(cat /run/picoclaw.pid) | head -n1)
