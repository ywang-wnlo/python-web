# Flaskr

The basic blog app built in the Flask [tutorial](https://flask.palletsprojects.com/tutorial/).

## Install

Create a virtualenv and activate it:

```bash
python3 -m venv .venv
.venv/bin/activate
```

Or on Windows cmd:

```cmd
python3 -m venv .venv
.venv\Scripts\activate.bat
```

Install Flaskr:

```bash
pip install flask
```

## Run in debug

```bash
flask --app flaskr init-db
flask --app flaskr run --debug
```

Open http://127.0.0.1:5000 in a browser.

## Production environment (Docker)

Build the image:

```bash
docker build -t python-web .
```

Initialize the database:

```bash
docker run -p [port]:8080 -it --restart unless-stopped --name python-web python-web
```

After db initialization, ctrl+c to stop the container

Normally, you can run the container with:

```bash
docker start python-web
```
