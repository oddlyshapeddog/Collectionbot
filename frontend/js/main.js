function init() {
    return new Promise((resolve, reject) => {
        console.log("Initializing");
        Config.loadConfig()
            .then(() => {
                console.log("Config loaded");
                Auth.init()
                    .then(() => {
                        console.log(
                            "Auth loaded; " +
                            (Auth.isLoggedIn() ?
                                `Logged in as ${Auth.getUserData("name")}` :
                                "Not logged in")
                        );
                        document.querySelector("#app").innerHTML = "";
                        resolve();
                    })
                    .catch(reject);
            })
            .catch(reject);
    });
}