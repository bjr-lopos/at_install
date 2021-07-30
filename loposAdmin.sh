#!/bin/bash
#visudo mike ALL=(ALL) NOPASSWD: /home/lopos/install/loposAdmin.sh
#whoami
cd /home/lopos/install
export PYTHONPATH="/usr/lib/python36.zip:/usr/lib/python3.6:/usr/lib/python3.6/lib-dynload:/home/lopos/.local/lib/python3.6/site-packages:/usr/local/lib/python3.6/dist-packages:/usr/lib/python3/dist-packages"
#echo $PYTHONPATH
python3 loposAdmin.py $*
