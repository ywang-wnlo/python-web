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

## Run

```bash
flask --app flaskr init-db
flask --app flaskr run --debug
```

Open http://127.0.0.1:5000 in a browser.
