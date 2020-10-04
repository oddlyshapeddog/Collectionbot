const Auth = (function() {
  const authProvider = "discord"; // hardcoded for now
  let isLoggedIn = false;
  let authResponse = null;
  let userData = {};

  const DISCORD_LOGIN_URL =
    "https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=268553280&redirect_uri=https%3A%2F%2Flocalhost%3A8000%2Fdashboard.html&response_type=code&scope=identify%20guilds%20bot%20messages.read";

  function fetchUserData() {
    return new Promise((resolve, reject) => {
      const endpoint = `https://discord.com/api/users/@me`;
      const headers = {
        Authorization: "Bearer " + authResponse.access_token
      };
      Utils.makeHttpRequest("GET", endpoint, undefined, headers)
        .then(body => {
          if (
            body &&
            body.id &&
            body.username &&
            body.discriminator &&
            body.avatar
          ) {
            resolve({
              provider: "discord",
              id: body.id,
              username: body.username,
              discriminator: body.discriminator,
              name: body.username + "#" + body.discriminator,
              avatar: `https://cdn.discordapp.com/avatars/${body.id}/${body.avatar}.png?size=56`
            });
          } else {
            reject("Invalid Discord response; missing fields");
          }
        })
        .catch(reject);
    });
  }

  function init() {
    return new Promise((resolve, reject) => {
      parseHashParams();
      if (hasValidAuthResponse()) {
        fetchUserData()
          .then(data => {
            console.log("User data:");
            console.log(data);
            Object.assign(userData, data);
            isLoggedIn = true;
            resolve();
          })
          .catch(reject);
      } else {
        resolve();
      }
    });
  }

  function hasValidAuthResponse() {
    return (
      authResponse &&
      authResponse.token_type === "Bearer" &&
      authResponse.access_token &&
      authResponse.expires_in
    );
  }

  function parseHashParams() {
    if (location.hash) {
      const hashString = location.hash.replace(/^#/, "");
      const hashSplit = hashString.split("&");
      const hashObj = hashSplit.reduce((acc, current) => {
        let [k, v] = current.split("=");
        v = decodeURIComponent(v);
        acc[k] = v;
        return acc;
      }, {});
      authResponse = hashObj;
    }
  }

  return {
    DISCORD_LOGIN_URL: DISCORD_LOGIN_URL,
    init: init,
    isLoggedIn: () => !!isLoggedIn,
    getAuthData: k => authResponse[k],
    getUserData: k => userData[k]
  };
})();
