#!"c:\users\ben goffer\pycharmprojects\dropship_scrapper-\venv\scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'myawis==0.2.4','console_scripts','myawis'
__requires__ = 'myawis==0.2.4'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('myawis==0.2.4', 'console_scripts', 'myawis')()
    )
