@echo off
echo ====================================================
echo Starting MongoDB Server (port 27017)...
echo ====================================================
"C:\Program Files\MongoDB\Server\8.3\bin\mongod.exe" --dbpath "%~dp0backend\mongo_data" --bind_ip 127.0.0.1 --port 27017 --wiredTigerCacheSizeGB 0.25 --setParameter diagnosticDataCollectionEnabled=false
pause
