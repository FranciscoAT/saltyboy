const express = require('express');
const bodyParser = require('body-parser');

// Routers
const insertRouter = require('./routes/insert');

const app = express();
const port = 8080;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.use('/insert', insertRouter);

app.listen(port, (err) => {
    if (err) {
        return console.log("Something went wrong.", err);
    }

    console.log("Now listening on:", port);
});
