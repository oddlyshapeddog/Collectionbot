function Breadcrumbs(props) {
    const { h, render } = preact;
    const html = htm.bind(h);
    const crumbs = Routing.getBreadcrumbs().map(
        ({ pageId, url, name }) =>
        html `
        <li>
          <a class="breadcrumb-link breadcrumb-link-${pageId}" href="${url}"
            >${name}</a
          >
        </li>
      `
    );
    return html `
    <nav class="breadcrumb" aria-label="breadcrumbs">
      <div class="container">
        <ul>
          ${crumbs}
        </ul>
      </div>
    </nav>
  `;
}