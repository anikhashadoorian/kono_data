#!/usr/bin/env bash
cd kono-data-frontend
npm install
ionic build --prod -- --base-href /static/ionic/
rm -rf ../data_model/static/ionic/
mkdir ../data_model/static/ionic/
cp -rf www/* ../data_model/static/ionic/
cd ..
