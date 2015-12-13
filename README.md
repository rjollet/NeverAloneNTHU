# NeverAloneNTHU

Project for Advance Database class at NTHU we create a dating app using a Graph DB. 
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/rjollet-/NeverAloneNTHU?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

## Get started

If you want to clean your previous docker image
```
docker-compose rm
```
To build the image for django

```
docker-compose build
```
Torun our project

```
docker-compose up
```

## [Django](https://docs.djangoproject.com/en/1.9/)

To create a new project
```
$ docker-compose run web django-admin.py startproject neveralone .

```

To create a new app
```
docker-compose run web python manage.py startapp app
```

Afeter generating a project or app you may need to change the ownership
```
sudo chown -R $USER:$USER .
```