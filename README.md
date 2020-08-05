# Indice pollution

This package give you access to air pollution level in France.

You can instantiate a small website with a search bar, to search the air pollution level for a specific city, or you can use it as a lib.

## Website

Make a new virtual environment, and install the package with

```
pip install indice_pollution
```

And then run flask

```
flask run
```

Access it at `http://localhost:5000`

## As a lib


Make a new virtual environment, and install the package with

```
pip install indice_pollution
```

And then you can use it with

```
from indice_pollution import forecast
forecast(75101)
```