@ECHO OFF

REM Dump wq configuration object to file (requires Django 1.7)
python db/manage.py dump_config --format amd > app/js/data/config.js

REM Build javascript with wq.app
CD app
wq build %1 || exit /b
CD ..

REM Force important files through any unwanted server caching
REM sed -i "s/wyobio.js/wyobio.js?v="$1"/" htdocs-build/wyobio.appcache
REM sed -i "s/wyobio.css/wyobio.css?v="$1"/" htdocs-build/wyobio.appcache

REM Preserve Django's static files (e.g. admin)
REM if [ -d htdocs/static ]; then
REM    cp -a htdocs/static htdocs-build/static
REM fi;

REM Replace existing htdocs with new version
RMDIR htdocs /S /Q
RENAME htdocs-build htdocs

REM Restart Django
NET STOP apache2.4
NET START apache2.4
