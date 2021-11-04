#!/bin/bash
#visudo mike ALL=(ALL) NOPASSWD: /home/lopos/install/loposAdmin.sh
#whoami
cd /home/lopos/install
export PYTHONPATH=`python -c "import site, os; print(os.path.join(site.USER_BASE, 'lib', 'python', 'site-packages'))"`
echo $PYTHONPATH
python3 loposAdmin.py $*
