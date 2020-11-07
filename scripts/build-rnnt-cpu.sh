#!/bin/bash

mkdir -p externals && cd externals

if [ ! -d warp-transducer ]; then
    git clone https://github.com/usimarit/warp-transducer.git
fi
cd ./warp-transducer
mkdir -p build && cd build
cmake \
-DUSE_NAIVE_KERNEL=on \
-DCMAKE_C_COMPILER_LAUNCHER="$(which gcc)" \
-DCMAKE_CXX_COMPILER_LAUNCHER="$(which g++)"  \
..

make
cd ../tensorflow_binding
python3 setup.py install --user

wget -qO-  https://raw.githubusercontent.com/usimarit/warp-transducer/master/tensorflow_binding/tests/test_basic.py | python3 -