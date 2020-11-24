#!/bin/bash

cd testspace

g++ -o boggle.exe -std=c++17 boggle.c lexicon.c 2> error.msg

if [[ $? == 0 ]]; then
    echo "Compilation: pass"
else
    echo "Compilation: failed with the following message: "
    cat error.msg
fi
