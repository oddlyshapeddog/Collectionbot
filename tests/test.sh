#!/bin/bash

if [ -z "$1" ]; then
  echo -e "WARNING!!\nYou need to pass the DISCORD_WEKHOOK_URL_CANARY environment variable as the first argument to this script." && exit
fi

echo -e "[Webhook]: Sending webhook to Discord...\\n";

WEBHOOK_DATA='{
  "username": "",
  "avatar_url": "",
  "content": "!runhouse"
}'

(curl --fail --progress-bar -A "TravisCI-Webhook" -H Content-Type:application/json -H X-Author:NotDaisuke -d "${WEBHOOK_DATA//	/ }" "$1" \
  && echo -e "[Webhook]: Successfully sent the webhook.") || echo -e "[Webhook]: Unable to send webhook."