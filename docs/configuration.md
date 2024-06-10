# Configuration

This file shows the different configuration options for your Provenance Application. The W3C Data Model consists of three types: *[Entities](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-entity), [Agents](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-agent) and [Activities](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-Activity)*.  

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
