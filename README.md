# Primitize

Primitize is a library that facilitates converting dataclass instances into primitive objects. It provides facilites to massage the data, validate it and write it out to file in pretty much any format you would want.

# Example usage
## Generating configuration files
Imagine we want to generate configuration files for several clusters, we have good sensible defaults but nothing is always exactly the same. In this example, we want each cluster configuration to be written in a json file.

```python
from dataclasses import dataclass
from enum import Enum
import json

from primitize.core import primitize, primitized


class HostType(Enum):
    COMPUTE = "Compute"
    WEB = "Web"
    STORAGE = "Storage"


@dataclass
class User:
    username: str


@dataclass
class Cluster:
    name: str
    size: int = primitized(validator=lambda v, o: v > 0)
    host_type: HostType = primitized(
        default=HostType.WEB, modifier=lambda v, o: v.value
    )
    admins: Set[User] = primitized(
        default_factory=set,
        modifier=lambda v, o: sorted(x),
        validator: lambda v, o: len(x) > 0,
    )



clusters ={
    Cluster("A", 3, HostType.COMPUTE, {User("root")}),
    Cluster("B", 3, admins={User("root")}),
    Cluster("C", 3, HostType.STORAGE, {User("foo")}),
}

for cluster in clusters:
    prim = primitize(cluster)
    payload = json.dumps(prim, sort_keys=True, indent=4)
    with (Path(".") / "output" / f"{cluster.name}.json").open("w") as fd:
        fd.write(payload)
```

Upon executing this, you will find the following files under `./output/`:

`./output/A.json`:
```
{
    "name": "A",
    "size": 3,
    "host_type": "Compute",
    "admins": [
        "root"
    ]
}
```

`./output/B.json`:
```
{
    "name": "A",
    "size": 3,
    "host_type": "Web",
    "admins": [
        "root"
    ]
}
```

`./output/C.json`:
```
{
    "name": "C",
    "size": 3,
    "host_type": "Storage",
    "admins": [
        "foo"
    ]
}
```


# How is this different from X ?

|                        |   Primitize   | Protobuf/Thrift | TypedDict |   Jinja    |
|------------------------|---------------|-----------------|-----------|------------|
| Modifiers              |      Yes      |       No        |    No     |     No     |
| Validators             | Type & Custom |      Type       |   Type    |     No     |
| Language support       |  Python only  |    Multiple     |  Python   | Custom DSL |
| Full Python API        |      Yes      |       No        |    Yes    |     No     |
| Format flexibility     |      Yes      |       No        |    No     |     Yes    |

* Modifiers: Primitize allows you to define functions that will massage the values prior to serialization, this allows your to rename, or reformat data to make the serialization easier. A typical usecase for this is to have the values of a type that is easy to manipulate and use a modifier to rewrite it to the what your end format expects
* Validators: Primitize uses standard Python typing so mypy will ensure you have type checking. In Primitize you can also define functions that allows you to ensure that the value is correct upon serialization.
* Language support: Primitize is a python library, as such it is primarily useful in Python.
* Full Python API: Unlike a restrictive DSL, with Primitize it is really just your Python program running, so you can do whatever you want, we just help you convert dataclasses into primitive types so it is easier to write out.
* Format flexibility: Primitize doesn't write data out for you so you can write it out as anything you want. Do you want json ? `json.dumps(primitize(data))` Do you want yaml ? `yaml.dumps(primitize(data))`. It's that simple.