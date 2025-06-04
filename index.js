const express = require('express')
const bodyParser = require('body-parser')
const fileUpload = require('express-fileupload');
//require('dotenv').config()
//console.log(process.env)
//const config = require('config');
const cors = require('cors');

const app = express();

app.use(cors()) //and this


// enable files upload
app.use(fileUpload({
    createParentPath: true
}));

var myArgs = process.argv.slice(2);
if(myArgs.length>0){
    env = myArgs[0]
}
env ="development"
console.log(__dirname+ '/config/config')
const config = require(__dirname + '/config/config.js')[env];
console.log(config)
console.log('host: ' + config.dbHost)


app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({extended: true})); // support encoded bodies
//const PORT = config.get("myPort")

const projectRoutes = require('./routes/project');
const userRoutes = require('./routes/user');

const indexRoutes = require('./routes/index');

app.use('/', indexRoutes);
app.use('/project', projectRoutes);
app.use('/user', userRoutes);


app.get('/*', function(req, res) {
    res.send('Not implemented');
});

app.listen(3000, function () {
    console.log('Server is running at PORT:', 3000);
});


//
//yarn sequelize-cli model:generate --name User --attributes username:string,firstname:string,lastname:string,password:string
//yarn db:g:seed users
//yarn db:g:migration addPassword
//psql -h localhost -U admin -d db -p 5432 -a -f config.js/populate.sql
//yarn sequelize-cli model:generate --name usera --attributes username:string,firstname:string,lastname:string,password:string
/*    "bcrypt": "^5.0.1",
    "body-parser": "^1.19.0",
    "config": "^3.3.7",
    "cors": "^2.8.5",
    "dotenv": "^16.0.0",
    "express": "^4.17.1",
    "express-fileupload": "^1.3.1",
    "jsonwebtoken": "^8.5.1",
    "n": "^8.2.0",
    "neo4j-driver": "^4.4.5"*/
