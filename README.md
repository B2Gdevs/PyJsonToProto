# PyJsonToProto
> Thanks for checking out PyJsonToProto, this is a port of https://github.com/json-to-proto/json-to-proto.github.io in to Python to be used in a number of applications using Protobufs

## Installation
> This package is published as a pip installable package.

```bash
pip install py_json_to_proto
```

## How to use

### CLI usage
> The CLI is the name of the project abbreviated as `jsp`.  Why? Try typing `py_json_to_proto`
> a ton of times

**HELP:**
```bash
usage: jsp.exe [-h] [--google_timestamp GOOGLE_TIMESTAMP] [--inline INLINE] [--input_file INPUT_FILE] [--output_file OUTPUT_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --google_timestamp GOOGLE_TIMESTAMP
                        Add timestamp to imports if in json
  --inline INLINE       unsure...this could use a contribution
  --input_file INPUT_FILE, -i INPUT_FILE
                        The input file to convert
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        The location to save the protos
```


```bash
jsp --input_file="test.json" --output_file="yolo.proto"
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
from py_json_to_proto.convert import convert, Options

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