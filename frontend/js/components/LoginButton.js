function LoginButton(props) {
    const { h, render } = preact;
    const html = htm.bind(h);
    const clientId = Config.get("discordClientId");
    const scope = encodeURIComponent(
        ["identify", "guild", "bot", "messages.read"].join(" ")
    );
    const loginUrl = Auth.DISCORD_LOGIN_URL.replace("CLIENT_ID", clientId);
    const logoutUrl = `index.html`;

    if (!Auth.isLoggedIn()) {
        return html `
      <a class="button is-inverted state--not-logged-in" href="${loginUrl}">
        <span class="icon">
          <i class="fab fa-discord"></i>
        </span>
        <span>Sign in with Discord</span>
      </a>
    `;
    } else {
        const name = Auth.getUserData("name");
        const avatar = Auth.getUserData("avatar");
        return html `
      <img src="${avatar}" /> <span>${name}</span>
      <a class="button is-text state--logged-in" href="${logoutUrl}">
        <span>Sign out</span>
      </a>
    `;
    }
}