#!/bin/bash
brew update
brew install ccache openssl
#cd /usr/local/include
#ln -s ../opt/openssl/include/openssl
#cd ~
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig"

git clone https://github.com/MacPython/terryfy.git ~/terryfy
source ~/terryfy/travis_tools.sh
get_python_environment macpython $TRAVIS_PYTHON_VERSION ~/macpython_venv
source ~/macpython_venv/bin/activate
pip install virtualenv
