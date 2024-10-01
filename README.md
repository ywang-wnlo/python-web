# Flaskr

The basic blog app built in the Flask [tutorial](https://flask.palletsprojects.com/tutorial/).

## Install

**Be sure to use the same version of the code as the version of the docs
you're reading.** You probably want the latest tagged version, but the
default Git version is the main branch.

```bash
# clone the repository
$ git clone https://github.com/pallets/flask
$ cd flask
# checkout the correct version
$ git tag  # shows the tagged versions
$ git checkout latest-tag-found-above
$ cd examples/tutorial
```

Create a virtualenv and activate it:

```bash
$ python3 -m venv .venv
$ . .venv/bin/activate
```

Or on Windows cmd:

```cmd
$ py -3 -m venv .venv
$ .venv\Scripts\activate.bat
```

Install Flaskr:

```bash
$ pip install -e .
```

Or if you are using the master branch, install Flask from source before installing Flaskr:

```bash
$ pip install -e ../..
$ pip install -e .
```

## Run

```bash
$ flask --app flaskr init-db
$ flask --app flaskr run --debug
```

Open http://127.0.0.1:5000 in a browser.
