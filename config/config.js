require('dotenv').config();
module.exports = {
    "development": {
        "username": 'neo4j',
        "password": 'test1234',
        "database": "postgres",
        "host": '127.0.0.1',
        "port": 5432,
        "my_port": 3000,
        "dialect": 'postgres',
        "secret": 'IHaveASecurePassword',

        "dbHost":"neo4j://localhost:7687",
        "dbUser":"neo4j",
        "dbPass":"test1234"
    },
    "test": {
        "username": 'neo4j',
        "password": 'test1234',
        "database": "postgres",
        "host": '127.0.0.1',
        "port": 5432,
        "my_port": 3000,
        "dialect": 'postgres',
        "secret": 'IHaveASecurePassword',

        "dbHost":"neo4j://localhost:7687",
        "dbUser":"neo4j",
        "dbPass":"test1234"
    },
    "production": {
        "username": 'admin',
        "password": 'admin',
        "database": "postgres",
        "host": 'postgres',
        "port": 5432,
        "my_port": 3000,
        "dialect": 'postgres',
        "secret": 'IHaveASecurePassword',

        "dbUser":"neo4j",
        "dbPass":"test1234",
        "dbHost":"neo4j://localhost:7687",

    }
}
