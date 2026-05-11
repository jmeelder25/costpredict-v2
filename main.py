==> It looks like we don't have access to your repo, but we'll try to clone it anyway.
Menu
==> Cloning from https://github.com/jmeelder25/costpredict-v2
==> Checking out commit 89f7014a65adb9e91ac29986db5e51045df2cb11 in branch main
==> Using Python version 3.11.0 via environment variable PYTHON_VERSION
==> Docs on specifying a Python version: https://render.com/docs/python-version
==> Installing Python version 3.11.0...
==> Using Poetry version 2.1.3 (default)
==> Docs on specifying a Poetry version: https://render.com/docs/poetry-version
==> Running build command 'pip install -r requirements.txt'...
Collecting flask==3.0.2
  Downloading flask-3.0.2-py3-none-any.whl (101 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 101.3/101.3 kB 4.8 MB/s eta 0:00:00
Collecting gunicorn==21.2.0
  Downloading gunicorn-21.2.0-py3-none-any.whl (80 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 80.2/80.2 kB 7.2 MB/s eta 0:00:00
Collecting weasyprint==61.2
  Downloading weasyprint-61.2-py3-none-any.whl (271 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 271.5/271.5 kB 9.1 MB/s eta 0:00:00
Collecting pydyf==0.9.0
  Downloading pydyf-0.9.0-py3-none-any.whl (7.9 kB)
Collecting fonttools==4.49.0
  Downloading fonttools-4.49.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 19.6 MB/s eta 0:00:00
Collecting Pillow==10.2.0
  Downloading pillow-10.2.0-cp311-cp311-manylinux_2_28_x86_64.whl (4.5 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 40.9 MB/s eta 0:00:00
Collecting pandas==2.2.1
  Downloading pandas-2.2.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (13.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 13.0/13.0 MB 68.9 MB/s eta 0:00:00
Collecting requests==2.31.0
  Downloading requests-2.31.0-py3-none-any.whl (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.6/62.6 kB 17.6 MB/s eta 0:00:00
Collecting python-dotenv==1.0.1
  Downloading python_dotenv-1.0.1-py3-none-any.whl (19 kB)
Collecting Werkzeug>=3.0.0
  Downloading werkzeug-3.1.8-py3-none-any.whl (226 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 226.5/226.5 kB 53.4 MB/s eta 0:00:00
Collecting Jinja2>=3.1.2
  Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 134.9/134.9 kB 33.6 MB/s eta 0:00:00
Collecting itsdangerous>=2.1.2
  Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Collecting click>=8.1.3
  Downloading click-8.3.3-py3-none-any.whl (110 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 110.5/110.5 kB 25.0 MB/s eta 0:00:00
Collecting blinker>=1.6.2
  Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
Collecting packaging
  Downloading packaging-26.2-py3-none-any.whl (100 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.2/100.2 kB 25.6 MB/s eta 0:00:00
Collecting cffi>=0.6
  Downloading cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (215 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 215.6/215.6 kB 50.5 MB/s eta 0:00:00
Collecting html5lib>=1.1
  Downloading html5lib-1.1-py2.py3-none-any.whl (112 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 112.2/112.2 kB 32.8 MB/s eta 0:00:00
Collecting tinycss2>=1.0.0
  Downloading tinycss2-1.5.1-py3-none-any.whl (28 kB)
Collecting cssselect2>=0.1
  Downloading cssselect2-0.9.0-py3-none-any.whl (15 kB)
Collecting Pyphen>=0.9.1
  Downloading pyphen-0.17.2-py3-none-any.whl (2.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 98.2 MB/s eta 0:00:00
Collecting fonttools[woff]>=4.0.0
  Downloading fonttools-4.62.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.1/5.1 MB 97.9 MB/s eta 0:00:00
Collecting numpy<2,>=1.23.2
  Downloading numpy-1.26.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (18.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 18.3/18.3 MB 81.7 MB/s eta 0:00:00
Collecting python-dateutil>=2.8.2
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 229.9/229.9 kB 57.0 MB/s eta 0:00:00
Collecting pytz>=2020.1
  Downloading pytz-2026.2-py2.py3-none-any.whl (510 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 510.1/510.1 kB 69.7 MB/s eta 0:00:00
Collecting tzdata>=2022.7
  Downloading tzdata-2026.2-py2.py3-none-any.whl (349 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 349.3/349.3 kB 66.2 MB/s eta 0:00:00
Collecting charset-normalizer<4,>=2
  Downloading charset_normalizer-3.4.7-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (214 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 214.1/214.1 kB 53.7 MB/s eta 0:00:00
Collecting idna<4,>=2.5
  Downloading idna-3.14-py3-none-any.whl (72 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 72.2/72.2 kB 23.2 MB/s eta 0:00:00
Collecting urllib3<3,>=1.21.1
  Downloading urllib3-2.7.0-py3-none-any.whl (131 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 131.1/131.1 kB 37.4 MB/s eta 0:00:00
Collecting certifi>=2017.4.17
  Downloading certifi-2026.4.22-py3-none-any.whl (135 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 135.7/135.7 kB 41.0 MB/s eta 0:00:00
Collecting pycparser
  Downloading pycparser-3.0-py3-none-any.whl (48 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.2/48.2 kB 14.8 MB/s eta 0:00:00
Collecting webencodings
  Downloading webencodings-0.5.1-py2.py3-none-any.whl (11 kB)
Collecting fonttools[woff]>=4.0.0
  Downloading fonttools-4.62.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.1/5.1 MB 128.4 MB/s eta 0:00:00
  Downloading fonttools-4.61.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 127.1 MB/s eta 0:00:00
  Downloading fonttools-4.61.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 122.7 MB/s eta 0:00:00
  Downloading fonttools-4.60.2-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 116.8 MB/s eta 0:00:00
  Downloading fonttools-4.60.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 123.6 MB/s eta 0:00:00
  Downloading fonttools-4.60.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 100.1 MB/s eta 0:00:00
  Downloading fonttools-4.59.2-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 130.0 MB/s eta 0:00:00
  Downloading fonttools-4.59.1-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 130.1 MB/s eta 0:00:00
  Downloading fonttools-4.59.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 132.0 MB/s eta 0:00:00
  Downloading fonttools-4.58.5-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 132.4 MB/s eta 0:00:00
  Downloading fonttools-4.58.4-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 131.5 MB/s eta 0:00:00
  Downloading fonttools-4.58.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.0/5.0 MB 129.7 MB/s eta 0:00:00
  Downloading fonttools-4.58.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 128.6 MB/s eta 0:00:00
  Downloading fonttools-4.58.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 130.9 MB/s eta 0:00:00
  Downloading fonttools-4.58.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 120.4 MB/s eta 0:00:00
  Downloading fonttools-4.57.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 130.8 MB/s eta 0:00:00
  Downloading fonttools-4.56.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 124.9 MB/s eta 0:00:00
  Downloading fonttools-4.55.8-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 123.5 MB/s eta 0:00:00
  Downloading fonttools-4.55.7-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 127.9 MB/s eta 0:00:00
  Downloading fonttools-4.55.6-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 122.9 MB/s eta 0:00:00
  Downloading fonttools-4.55.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 107.8 MB/s eta 0:00:00
  Downloading fonttools-4.55.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 114.3 MB/s eta 0:00:00
  Downloading fonttools-4.55.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 131.3 MB/s eta 0:00:00
  Downloading fonttools-4.55.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 84.5 MB/s eta 0:00:00
  Downloading fonttools-4.55.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 121.1 MB/s eta 0:00:00
  Downloading fonttools-4.55.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 132.2 MB/s eta 0:00:00
  Downloading fonttools-4.54.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 124.5 MB/s eta 0:00:00
  Downloading fonttools-4.54.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 90.5 MB/s eta 0:00:00
  Downloading fonttools-4.53.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 114.2 MB/s eta 0:00:00
  Downloading fonttools-4.53.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 113.6 MB/s eta 0:00:00
  Downloading fonttools-4.52.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 123.1 MB/s eta 0:00:00
  Downloading fonttools-4.52.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 114.7 MB/s eta 0:00:00
  Downloading fonttools-4.52.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 120.2 MB/s eta 0:00:00
  Downloading fonttools-4.51.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 117.2 MB/s eta 0:00:00
  Downloading fonttools-4.50.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.9/4.9 MB 82.4 MB/s eta 0:00:00
Collecting zopfli>=0.1.4
  Downloading zopfli-0.4.1-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (829 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 829.4/829.4 kB 77.3 MB/s eta 0:00:00
Collecting brotli>=1.0.1
  Downloading brotli-1.2.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.4/1.4 MB 87.7 MB/s eta 0:00:00
Collecting six>=1.9
  Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Collecting MarkupSafe>=2.0
  Downloading markupsafe-3.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Installing collected packages: webencodings, pytz, brotli, zopfli, urllib3, tzdata, tinycss2, six, python-dotenv, Pyphen, pydyf, pycparser, Pillow, packaging, numpy, MarkupSafe, itsdangerous, idna, fonttools, click, charset-normalizer, certifi, blinker, Werkzeug, requests, python-dateutil, Jinja2, html5lib, gunicorn, cssselect2, cffi, weasyprint, pandas, flask
Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Pillow-10.2.0 Pyphen-0.17.2 Werkzeug-3.1.8 blinker-1.9.0 brotli-1.2.0 certifi-2026.4.22 cffi-2.0.0 charset-normalizer-3.4.7 click-8.3.3 cssselect2-0.9.0 flask-3.0.2 fonttools-4.49.0 gunicorn-21.2.0 html5lib-1.1 idna-3.14 itsdangerous-2.2.0 numpy-1.26.4 packaging-26.2 pandas-2.2.1 pycparser-3.0 pydyf-0.9.0 python-dateutil-2.9.0.post0 python-dotenv-1.0.1 pytz-2026.2 requests-2.31.0 six-1.17.0 tinycss2-1.5.1 tzdata-2026.2 urllib3-2.7.0 weasyprint-61.2 webencodings-0.5.1 zopfli-0.4.1
[notice] A new release of pip available: 22.3 -> 26.1.1
[notice] To update, run: pip install --upgrade pip
==> Uploading build...
==> Uploaded in 3.3s. Compression took 3.2s
==> Build successful 🎉
==> Deploying...
==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
==> Exited with status 127
==> Common ways to troubleshoot your deploy: 
