#!/usr/bin/env bash
zappa update prod
zappa manage prod migrate
zappa manage prod "collectstatic --noinput"

# terminal-notifier -title "KonoData Deploy" -message "Done 🚀"
# zappa invoke prod "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'nimda')" --raw
# python manage.py dumpdata --format=json data_model > data_model/fixtures/initial_data.json
# zappa manage prod "loaddata data_model/fixtures/initial_data.json"
