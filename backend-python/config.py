mongo = dict(
    ports=27017,
    volumes='/data/db',
)
mysql = dict(
    ports=3306,
    volumes='/var/lib/mysql',
)
postgres = dict(
    ports=5432,
    volumes='/var/lib/postgresql',
)
