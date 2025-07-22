![pipeline](https://gitlab.dlr.de/ssa/django-prov/badges/main/pipeline.svg)
![coverage](https://gitlab.dlr.de/ssa/django-prov/badges/main/coverage.svg)

# django-prov

django-prov is a Django app to capture Provenance related data in your Django project. It complies to the [W3C PROV Data Model](https://www.w3.org/TR/2013/REC-prov-dm-20130430/).

## Setup

The package was built with Python 3.9 and uses the libraries [Django](https://www.djangoproject.com/) and [prov](https://prov.readthedocs.io/en/latest/). You can install it with:

```shell
pip install django-prov
```

## Usage

1. To use the app in your Django project, you have to add "django_prov" to the top of your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
   "django_prov",
   ...,
]
```

2. You are then able to configure the app to your needs by using the following in your settings. As there are many configuration options available, please see the [Configuration](docs/configuration.md) for more details. 

```python
PROVENANCE = {
    "ENTITIES": ["...",],
    "AGENTS": ["...", ],
    "NAMESPACES": {"...", },
    "OUTPUT": {"...", },
}
```

3. Import and initialize the ProvenanceGenerator where you want to capture "Activities". For further information see the [Configuration](docs/configuration.md#Activities):  

```python
from django_prov.generator import ProvenanceGenerator

generator = ProvenanceGenerator.get("")
```

4. Choose the output formats that fit to your needs. For the available formats see the [Configuration](docs/configuration.md#Serialization):

5. Start your work and the Prov-Documents will be generated into your specified directory.
