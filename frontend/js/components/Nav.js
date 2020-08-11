function Nav(props) {
    const { h, render } = preact;
    const html = htm.bind(h);
    const start = props.loggedIn ?
        Routing.getDashboardLinks().map(
            ({ pageId, url, name }) =>
            html `
            <div class="navbar-start">
              <a class="navbar-item navbar-item-${pageId}" href="${url}">
                ${name}
              </a>
            </div>
          `
        ) :
        null;
    return html `
    <nav class="navbar is-transparent is-spaced">
      <div class="container">
        <div class="navbar-brand">
          <a class="navbar-item" href="index.html">
            <img src="img/osd-logo.png" alt="Oddly Shaped Dog logo" />
            <span>Bot name</span>
            <span class="beta">Beta</span>
          </a>
          <span class="navbar-burger burger" data-target="navbarMenuHeroB">
            <span></span>
            <span></span>
            <span></span>
          </span>
        </div>
        <div id="navbarMenuHeroB" class="navbar-menu">
          ${start}
          <div class="navbar-end">
            <span class="navbar-item">
              <${LoginButton} />
            </span>
          </div>
        </div>
      </div>
    </nav>
  `;
}