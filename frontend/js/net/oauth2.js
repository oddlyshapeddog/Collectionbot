const OAuth2 = (function() {
    class Oauth2Provider {
        constructor(
            name, {
                oauth2Endpoint,
                clientId,
                clientSecret,
                additionalAuthorizeParams,
                additionalTokenParams
            }
        ) {
            this.name = name;
            this.oauth2Endpoint = oauth2Endpoint;
            this.clientId = clientId;
            this.clientSecret = clientSecret;
            this.additionalAuthorizeParams = additionalAuthorizeParams || {};
            this.additionalTokenParams = additionalTokenParams || {};
        }

        getUserData(access_token) {
            throw new Error('Not implemented')
        }
    }

    class DiscordProvider extends Oauth2Provider {
        constructor() {
            super(
                'discord', {
                    oauth2Endpoint: "https://discord.com/api/oauth2",
                    clientId: process.env.DISCORD_CLIENT_ID,
                    clientSecret: process.env.DISCORD_CLIENT_SECRET,
                    additionalAuthorizeParams: {
                        scope: DISCORD_SCOPES
                    },
                    additionalTokenParams: {
                        scope: DISCORD_SCOPES
                    },
                }
            )
        }

        getUserData(access_token) {
            return new Promise((resolve, reject) => {
                const endpoint = `https://discord.com/api/users/@me`;
                const headers = {
                    Authorization: "Bearer " + access_token
                };
                const body = await Utils.makeHttpRequest("GET", endpoint, undefined, headers);
                if (
                    body &&
                    body.id &&
                    body.username &&
                    body.discriminator &&
                    body.avatar
                ) {
                    return {
                        provider: "discord",
                        id: body.id,
                        name: body.username + "#" + body.discriminator,
                        avatar: `https://cdn.discordapp.com/avatars/${body.id}/${body.avatar}.png?size=56`
                    };
                } else {
                    throw new Error("Invalid Discord response; missing fields");
                }
            })
        }
    }

    const OAUTH2_PROVIDERS = {
        discord: new DiscordProvider(),
    }

    return {
        providers: OAUTH2_PROVIDERS
    }
})()