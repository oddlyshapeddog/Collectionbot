# Collectionbot

## Setup

Keep the following things handy, you'll need them:

- Go to your custom [Discord app](https://discord.com/developers/applications/741867546524909601) and copy the client ID and client secret. **Never share the client secret or publish it through code! It's a secret!**
- Go to your Discord server, copy the names of the channels you want the bot to live in. These are "submit channels". You can have as many as you want.
- Still in your Discord server, copy the name of the channel you want to use to manage the bot. This is your admin channel. There can be only one.
- Still in your Discord server, create a role named "Artbot admins" (or whatever you want). Copy the name of this role.
- Still in your Discord server, go to your Discord emojis and figure out which one you want to use as an "adore" emote. Copy the name.

Then do this:

- Open config.json
- Change NAME_OF_YOUR_DISCORD_SERVER to the name of your Discord server
- Change CHANNEL_ID to your submit channel. You cna have multiple submit channels, separated by commas.
- Change ADMIN_CHANNEL_ID to your admin channel.
- Change YOUR_DISCORD_KEY to your discord key.
- Change ADMIN_ROLES to the name of the admin role.
- Change ADORE_EMOJI to the name of your adore emote.

## Development

Install the necessary dependencies:

```
pip3 install --user discord logging concurrent simplejson asyncio pytz sqlalchemy apscheduler zipfile
```

### GUI

Then to start the user interface, run this:

```
python3 frontend.py
```

And go to [https://localhost:8000](https://localhost:8000)

We currently use a self-signed certificate for SSL. The first time you open the GUI, your browser might warn you that your connection is not private. You need to add an exception to your browser so it accepts the self-signed certificate.

- [How to add an exception in IE/Edge](https://medium.com/@ali.dev/how-to-trust-any-self-signed-ssl-certificate-in-ie11-and-edge-fa7b416cac68)
- other browsers TBD

### Bot

To start the bot, run this:

```
python3 artbot.py
```

## CI

### Webhooks setup

The test suite requires the following env variables:

| Name                         | Description                               |
| ---------------------------- | ----------------------------------------- |
| `DISCORD_WEKHOOK_URL_CANARY` | Runs the canary                           |
| `DISCORD_WEBHOOK_URL_BUILDS` | Posts build success/failure notifications |

**Note:** I mistyped `WEBHOOK` as `WEKHOOK` but I'm too lazy to fix it
