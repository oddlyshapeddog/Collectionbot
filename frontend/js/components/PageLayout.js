function PageLayout(props) {
    const { h, render } = preact;
    const html = htm.bind(h);
    const title = Routing.getPageName(Routing.getCurrentPage());
    const header = Routing.isHomepage() ?
        null :
        html `
        <${Nav} />
        <${Breadcrumbs} />
        <h1 class="is-sr-only">${title}</h1>
      `;
    return html `
    <div class="page-layout">
      ${header} ${props.children}
    </div>
  `;
}