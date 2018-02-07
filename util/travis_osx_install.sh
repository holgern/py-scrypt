#!/bin/bash
brew update
brew install ccache openssl

export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"

git clone https://github.com/MacPython/terryfy.git ~/terryfy
source ~/terryfy/travis_tools.sh
get_python_environment macpython $TRAVIS_PYTHON_VERSION ~/macpython_venv
source ~/macpython_venv/bin/activate
pip install virtualenv
