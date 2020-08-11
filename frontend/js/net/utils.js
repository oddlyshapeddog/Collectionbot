const Utils = (function() {
    function makeHttpRequest(method, url, data, headers) {
        return new Promise((resolve, reject) => {
            let body = "";

            const options = {
                method: method,
                mode: "cors",
                cache: "no-cache",
                headers: headers || {},
                redirect: "follow",
                referrerPolicy: "no-referrer"
            };

            if (data) {
                options.body = data;
                options.headers["Content-Type"] = "application/json";
            }

            console.log("OUTGOING_REQUEST: " + url);
            console.log("Headers: " + JSON.stringify(options.headers));
            console.log("Data: " + JSON.stringify(data));

            fetch(url, options)
                .then(res => {
                    console.log("OUTGOING_REQUEST_RESPONSE: " + res);
                    console.log("Status: " + res.status + " " + res.statusText);
                    if (res.ok) {
                        res
                            .json()
                            .then(jsonObj => {
                                resolve(jsonObj);
                            })
                            .catch(e => {
                                reject(e);
                            });
                    } else {
                        reject(res.statusText);
                    }
                })
                .catch(reject);
        });
    }

    return {
        makeHttpRequest: makeHttpRequest
    };
})();