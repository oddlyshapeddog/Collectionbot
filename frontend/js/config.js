const Config = (function() {
    const COMPONENTS = {
        collectionbot: {
            name: "Collectionbot",
            description: "Configure and manage Collectionbot"
        }
    };

    const CONFIG = {};

    function get(k) {
        return CONFIG[k];
    }

    function loadConfig() {
        return new Promise((resolve, reject) => {
            Utils.makeHttpRequest("GET", "/api/config")
                .then(data => {
                    Object.assign(CONFIG, data);
                    resolve();
                })
                .catch(e => {
                    reject(e);
                });
        });
    }

    return {
        components: COMPONENTS,
        get: get,
        loadConfig: loadConfig
    };
})();