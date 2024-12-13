# Configuration

This file shows the different configuration options for your Provenance Application. The W3C Data Model consists of three types: *[Entities](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-entity), [Agents](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-agent) and [Activities](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-Activity)*.  

## Namespaces

To capture different applications in your project, you need to declare the namespaces for the apps. The default namespace can be set through your ROOT_URLCONF or declared manually. It is mandatory.


```python
PROVENANCE = {
    "NAMESPACES": {
            "DEFAULT": f"{ROOT_URLCONF.split('.')[0]}.org/",
            # or
            "DEFAULT": "yourproject.org/",
        },
}
```

The extra namespaces contain all apps you want to capture. This can include django specific apps, e.g. the "auth" app to capture user information. You can also add system specific information by adding "sys". If you want to capture Djangos Template view classes, you have to add "django" to the list.

```python
PROVENANCE = {
    "NAMESPACES": {
            "EXTRA": [
                # if you want to capture auth.User objectinfo, add 'auth'
                "auth",
                # if you want to capture django specific view classes, add 'django'
                "django",
                # if you want to capture system specific information, add 'sys'
                "sys",
                "yourapp1",
                "yourapp2",
                "django_prov"
        ]
            
        },
}
```

## Entities
You can declare which of your models you want to track as an entity by using the 'ENTITIES' Key in the Provenance Dictionary in your settings:

```python
PROVENANCE = {
    "ENTITIES": [
            "yourapp.ClassX",
            "...",
        ],
}
```

## Agents

You can also declare, which of your models you want to track as an Agent, e.g. persons or institutions.  

```python
PROVENANCE = {
    "AGENTS": [
            "yourapp.ClassY",
            "...",
        ],
}
```

| !!  Make sure to not declare a Class as an Entity and an Agent at the same time. This would distort the resulting data. !! |
|----------------------------------------------------------------------------------------------------------------------------|


## Other
There are other settings you can configure:
```python
PROVENANCE = {
    "OTHER": {
        "MAX_ARG_LENGTH": 100
    }
}
```

| Key            | Usage                                                                                                                  |
|----------------|------------------------------------------------------------------------------------------------------------------------|
| MAX_ARG_LENGTH | Passed args or kwargs to the func can be long. You can cut the record at a specific length to not overfill your storage |


## Activities

If you want to track the execution of Activites in your app, you have to use decorators for each function or Class itself. These decorators look different for the different cases:

1. You want to track your own functions:

```python
@generator.activity(name="foo")
def my_function():
    ...
```

2. You want to track Djangos built-in View Classes:

```python
@method_decorator(generator.activity(name="fooo",), name='dispatch')
class MyUpdateView(UpdateView):
    ...
```

## Serialization
To serialize your Prov Documents, you need to declare a path. 

```python
PROVENANCE = {
    "OUTPUT": {
            "PATH": f"your/path/",
        },
}
```

There are several serialization formats available:

```python
PROVENANCE = {
    "OUTPUT": {
            "SERIALIZE": [
                "n",
                "xml",
                "json",
                "rdf"
                ]
        },
}
```

## Graphical Output
It is also possible to plot your Prov Documents:

```python
PROVENANCE = {
    "OUTPUT": {
            "GRAPHIC": [
                "svg",
                "png",
                "pdf"
                ]
        },
}
```
