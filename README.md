# Welcome to NutriTrack!

This web-app builds off Miguel Grinberg's [Microblog v0.15](https://github.com/miguelgrinberg/microblog/tree/v0.15), allowing users to easily create and share meal plans and compare them to personalized nutrition recomendations, so that they can easily check a plan's macros and avoid nutritional deficiencies.

## How to use

The Docker container is available at *https://hub.docker.com/r/fgcharles/nutritrack*. With docker installed, the following commands will run the app configured to send emails through a gmail account and linked with MySQL database.

```
$ docker pull fgcharles/nutritrack

$ docker run --name mysql -d -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
    -e MYSQL_DATABASE=nutritrack -e MYSQL_USER=nutritrack \
    -e MYSQL_PASSWORD=<database-password> \
    mysql/mysql-server:latest

$ docker run --name nutritrack -d -p 8000:5000 --rm -e SECRET_KEY=my-secret-key \
    -e MAIL_SERVER=smtp.googlemail.com -e MAIL_PORT=587 -e MAIL_USE_TLS=true \
    -e MAIL_USERNAME=<your-gmail-username> -e MAIL_PASSWORD=<your-gmail-password> \
    --link mysql:dbserver \
    -e DATABASE_URL=mysql+pymysql://nutritrack:<database-password>@dbserver/nutritrack \
    nutritrack:latest
```

Things in angle brackets must be filled out. The app will then be available at *http://localhost:8000*.