#!/bin/bash

cd builder
git pull
bash addnewpackage.sh $1
git add .
git commit -m "auto: add package $1"
git push
