const Routing = (function() {
    const PAGE_NAMES = {
        index: "Home",
        dashboard: "Dashboard",
        "dashboard-discordbot": "Discord bot"
    };

    function getBaseHref() {
        const lastSlash = location.pathname.lastIndexOf("/");
        const baseHref = location.pathname.substr(0, lastSlash).replace(/\/$/, "");
        return baseHref;
    }

    function getCurrentPage() {
        const lastSlash = location.pathname.lastIndexOf("/");
        const filenameWithoutExtension = location.pathname
            .substr(lastSlash + 1)
            .replace(/\..*$/, "");
        return filenameWithoutExtension.toLowerCase();
    }

    function isActivePage(page) {
        return page === getCurrentPage();
    }

    function isCurrentPage(page) {
        return getCurrentPage.indexOf(page) === 0;
    }

    function getBreadcrumbs() {
        const cp = getCurrentPage();
        const split = cp.split("-");
        const crumbs = isHomepage() ?
            [] :
            [{
                pageId: "index",
                url: `${getBaseHref()}/index.html`,
                name: getPageName("index")
            }];
        const currentCrumb = [];
        for (let i = 0; i < split.length; i++) {
            currentCrumb.push(split[i]);
            const pageId = currentCrumb.join("-");
            const thisCrumb = {
                pageId: pageId,
                url: `${getBaseHref()}/${pageId}.html`,
                name: getPageName(pageId)
            };
            crumbs.push(thisCrumb);
        }
        return crumbs;
    }

    function getDashboardLinks() {
        return Object.keys(PAGE_NAMES)
            .filter(k => /^dashboard\-/)
            .map(k => ({
                pageId: k,
                url: `${getBaseHref()}/${k}.html`,
                name: PAGE_NAMES[k]
            }));
    }

    function getPageName(pageId) {
        if (pageId === "" || pageId === "/") {
            pageId = "index";
        }
        return PAGE_NAMES[pageId];
    }

    function isHomepage() {
        const cp = getCurrentPage();
        return cp === "index" || cp === "";
    }

    return {
        getBreadcrumbs: getBreadcrumbs,
        getCurrentPage: getCurrentPage,
        getDashboardLinks: getDashboardLinks,
        getPageName: getPageName,
        isActivePage: isActivePage,
        isCurrentPage: isCurrentPage,
        isHomepage: isHomepage
    };
})();