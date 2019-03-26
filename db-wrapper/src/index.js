const express = require('express');
const bodyParser = require('body-parser');

// Routers
const insertRouter = require(__dirname + '/routes/insert');
const oddsRouter = require(__dirname + '/routes/get-odds');

const app = express();
const port = 8080;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.use('/insert', insertRouter);
app.use('/oods', oddsRouter);


app.listen(port, (err) => {
    if (err) {
        return console.log("Something went wrong.", err);
    }

    console.log("Now listening on:", port);
});
