# Playbrush

## Django project setup steps

### Django project name

```
playbrush
```

### Models Create

### For database I used SQLite DB

I created a File model to store the uploaded csv files.

- csv1
- csv2

# To Run the project

### Clone git repo.

```
git clone https://github.com/buzzovi/playbrush.git
```

### Please navigate to the backend directory.

```
cd playbrush
```

### Installing virtualenv

On macOS and Linux:

```
python3 -m pip install --user virtualenv
```

On Windows:

```
py -m pip install --user virtualenv
```

### Create new python environment and activate it

On macOS and Linux:

```
python3 -m venv env
source env/bin/activate
```

On Windows:

```
py -m venv env
.\env\Scripts\activate
```

### Install Python requirements

```
pip install -r requirements.txt
python -m pip install --upgrade pip
```

### Run the server

```
python manage.py runserver
```

### Usefull links:

- Homepage http://127.0.0.1:8000
