let currentFightData;

chrome.runtime.onMessage.addListener((msg, sender, res) => {
    if (msg.action = 'newfight') {
        console.log("Recieved fighters: ", msg.value);
        updateFight(msg.value)
        .then((newData) => {
            res(newData);
        })
        .catch((error) => {
            res(error);
        });
    } else if (msg.action = 'getData') {
        res(currentFightData);
    }
});

function updateFight(fighters) {
    const fighter1 = fighters[0];
    const fighter2 = fighters[1];

    const url = encodeURI(`http://localhost:8080/odds?fighter1=${fighter1}&fighter2=${fighter2}`);

    return new Promise((resolve, reject) => {
        console.log("sending request to: ", url);
        let request = new XMLHttpRequest();
        request.open("GET", url);
        request.onload = () => {
            if (request.status >= 200 && request.status < 400) {
                console.log("Successful response", request.response);
                currentFightData = request.response;
                return resolve(request.response);
            }
            console.log("potential 404", request);
            return reject(request);
        }
        request.onerror = () => {
            console.log("bad response", request);
            reject(request);
        }

        request.send();
    });
}