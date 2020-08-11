function ComponentCard(props) {
    const { h, render } = preact;
    const html = htm.bind(h);
    const { componentId } = props;
    const url = `dashboard-${componentId}.html`;
    const { name, description } = Config.components[componentId];
    const indicator = html `
    <span class="icon has-text-success is-pulled-right">
      <i class="fas fa-toggle-on"></i>
      <span class="is-sr-only">Enabled</span>
    </span>
  `;
    return html `
    <div class="card">
      <div class="card-image">
        <a href="${url}">
          <figure class="image is-2by1">
            <img src="img/placeholder.jpg" role="presentation" />
          </figure>
        </a>
      </div>
      <div class="card-content">
        <h2 class="title is-4">
          <a href="${url}">${name}</a>
          ${indicator}
        </h2>
        <p>${description}</p>
      </div>
    </div>
  `;
}