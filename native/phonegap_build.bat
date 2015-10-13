@ECHO OFF

REM Dump wq configuration object to file (requires Django 1.7)
CD ..
python db/manage.py dump_config --format amd > app/js/data/config.js

REM Build javascript with wq.app
CD app
wq build %1 || exit /b
CD ../native

REM Replace existing build with new version
RMDIR build /S /Q
MKDIR build
MKDIR build\js
MKDIR build\js\lib
MKDIR build\css
MKDIR build\css\lib

COPY ..\htdocs-build\js\wyobio.js build\js\
COPY ..\htdocs-build\js\lib\require.js build\js\lib\
COPY ..\htdocs-build\css\wyobio.css build\css
XCOPY /S /I ..\htdocs-build\css\lib\images build\css\lib\images
XCOPY /S /I ..\htdocs-build\images build\images

wq mustache --template index.html --output build/index.html
wq mustache --template config.xml --output build/config.xml

COPY splash.png build\splash.png