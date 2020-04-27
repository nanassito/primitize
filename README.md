# Primitize

Primitize is a library that facilitates converting dataclass instances into primitive objects. It provides facilites to massage the data, validate it and write it out to file in pretty much any format you would want.

# Example usage
## Generating configuration files
Imagine we want to generate configuration files for several clusters, we have good sensible defaults but nothing is always exactly the same. In this example, we want each cluster configuration to be written in a json file.

```
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
    size: int = primitized(validator=lambda x: x > 0)
    host_type: HostType = primitized(default=HostType.WEB, modifier=lambda x: x.value)
    admins: Set[User] = primitized(
        default_factory=set,
        modifier=lambda x: sorted(x),
        validator: lambda x: len(x) > 0,
    )

    def prepare_primitization(self: "Cluster") -> None:
        """If this method exists, it is called as the first step of primitization.
        
        It is typical to perform x-fields updates here."""
        pass



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

## Why not use protobuf or thrift ?
Similar to protobuf and thrift, primitizer allows you to validate and serialize data. However you are in control of the serialization and the file format. Primitizer can easily generate pretty much any format (json, yaml, properties, xml, ini, etc.).

## Why no use jsonnet ?
Primitizer can generate any file format, just not json

## Why not jinja ?
Primitizer is full Python, so you have access to the entire API. As such you can do whatever you want with the objects to are manipulating.
Primitizer also offers strong validation primitives to allow you to check the data for errors before writing it out.
