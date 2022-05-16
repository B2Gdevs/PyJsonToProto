# PyJsonToProto
> Thanks for checking out PyJsonToProto, this is a port of https://github.com/json-to-proto/json-to-proto.github.io in to Python to be used in a number of applications using Protobufs

## How to use

### CLI usage

```bash
python cli.py --input_file="test.json" --output_file="yolo.proto"
```

The input file used
`test.json`

```json
{
    "id": 23357588,
    "node_id": "MDEwOlJlcG9zaXRvcnkyMzM1NzU4OA==",
    "name": "protobuf",
    "full_name": "protocolbuffers/protobuf",
    "private": false,
    "arg2": 1009,
    "arg1": 11124
  }
```

The output of the file
`yolo.proto`

```protobuf
syntax = "proto3";

message SomeMessage {
    uint32 id = 1;
    string node_id = 2;
    string name = 3;
    string full_name = 4;
    uint32 private = 5;
    uint32 arg2 = 6;
    uint32 arg1 = 7;
}
```

### Code Usage
> I would take a look at the cli code in `cli.py` to get a better feel.

```python
from convert import convert, Options

# Read in your json file and then convert to proto string
with open('test.json'), 'r') as file:
    data = convert(file.read(), Options(False, False))

# You're done, save the proto string
with open(args.output_file, 'w') as file:
    file.write(str(data))
```
___

### Authors:
* Benjamin Garrard