function HomepageHero(props) {
    const { h, render } = preact;
    const html = htm.bind(h);
    return html `
    <section class="hero is-medium">
      <div class="hero-head">
        <${Nav} />
      </div>
      <div class="hero-body">
        <div class="container">
          <h1 class="title">
            Bot name
          </h1>
          <p class="subtitle">
            Discord & Twitch utilities
          </p>
        </div>
      </div>
    </section>
  `;
}