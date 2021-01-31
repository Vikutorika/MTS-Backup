@echo off
:start
title GamerNoTitle's Minecraft Server - Start at %time%
java -Xmx2G -jar fabric-server-launch.jar --nogui
goto start