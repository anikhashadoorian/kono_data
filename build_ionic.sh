#!/usr/bin/env bash
cd kono-data-frontend
ionic build --prod -- --base-href /static/ionic/
mv www/* ../data_model/static/ionic