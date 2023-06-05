const express = require('express');
const compression = require('compression');
const mysql = require('mysql')
const config = require('./config');
const bodyParser = require('body-parser');
const cors = require('cors')

const db = mysql.createConnection(config.MySQLConnectionOption);
const port = process.env.port || process.env.PORT || 10086

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(compression());
app.use(cors());
app.options('*', cors());

const router = new express.Router()

router.post('/report', (req, res) => {
    const body = req.body;
    console.log(body);
    return res.send('{success: true}');
})

app.use('/', router);
app.listen(port, ()=>{
    console.log('Web Server Up!')
})