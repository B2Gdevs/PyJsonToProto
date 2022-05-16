import re
from typing import Any, Dict, List, Set
import json

google_any_import = "google/protobuf/any.proto";
google_timestamp_import = "google/protobuf/timestamp.proto";

google_any = "google.protobuf.Any";
google_timestamp = "google.protobuf.Timestamp";


class Result:
    """The result of the json to proto conversion."""
    def __init__(self, success: str, error: str) -> None:
        self._success: str = success
        self._error: str = error

    def __str__(self) -> str:
        return self._success


class ProtoPrimitiveType:
    """A model of a primitive found in a Proto."""
    def __init__(self, name: str, complex: bool = False, merge: bool = False) -> None:
        self._name: str = name
        self._complex: bool = complex
        self._merge: bool = merge



bool_proto_primitive_type = ProtoPrimitiveType("bool", False, False);
string_proto_primitive_type = ProtoPrimitiveType("string", False, False);
int64_proto_primitive_type = ProtoPrimitiveType("int64", False, True);
complex_proto_type = ProtoPrimitiveType(google_any, True, False);
timestamp_proto_type = ProtoPrimitiveType(google_timestamp, False, False);

class Options:
    """Unsure."""
    def __init__(self, inline: bool, google_proto_timestamp: bool):
        self._inline = inline
        self._google_proto_timestamp = google_proto_timestamp


class Collector:
    """Collects messages and imports."""
    def __init__(self) -> None:
        self._imports: Set[str] = set()
        self._messages: List[List[str]]  = [['']]
        self._message_name_suffix_counter: Dict[str, int] = {}

    def add_import(self, import_path: str):
        self._imports.add(import_path)

    def generate_unique_name(self, source: str) -> str:
        if self._message_name_suffix_counter.get(source):
            suffix = self._message_name_suffix_counter[source]
            self._message_name_suffix_counter[source] = suffix + 1;

            return f'{source}{suffix}'

        self._message_name_suffix_counter[source] = 1;

        return source;

    def add_message(self, lines: List[str]):
        self._messages.append(lines)

    def get_imports(self) -> Set[str]:
        return self._imports

    def get_messages(self) -> List[List[str]]:
        return self._messages


class Analyzer:
    def __init__(self, options: Options) -> None:
        self.options = options

    def analyze(self, json: Dict) -> str:
        if self.direct_type(json):
            return self.analyze_object({"first": json})

        if isinstance(json, List):
            return self.analyze_array(json)


        return self.analyze_object(json);

    def direct_type(self, value: Any) -> bool:

        if isinstance(value, str) or isinstance(value, float) or isinstance(value, int) or isinstance(value, bool):
            return True
        elif isinstance(value, dict):
            return value == None

        return False

    def analyze_array(self, array: List[Any]) -> str:
        inline_shift = self.add_shift()
        collector = Collector()
        lines = []
        type_name = self.analyze_array_property("nested", array, collector, inline_shift)
        lines.append(f'    {type_name} items = 1;')

        return render(collector.get_imports(), collector.get_messages(), lines, self.options);

    def analyze_object(self, json:  Dict) -> str:
        inline_shift = self.add_shift()
        collector = Collector()
        lines = []
        index = 1

        for key, value in json.items():
            type_name = self.analyze_property(key, value, collector, inline_shift)
            lines.append(f'    {type_name} {key} = {index};')

            index += 1

        return render(collector.get_imports(), collector.get_messages(), lines, self.options)

    def analyze_array_property(self, key: str, value: List[Any], collector: Collector, inline_shift: str) -> str:
        length = len(value)

        if length == 0:
            collector.add_import(google_any_import)

            return f'repeated {google_any}'

        first = value[0]
        if isinstance(first, list):
            collector.add_import(google_any_import)

            return f'repeated {google_any}'

        if length > 1:
            primitive = self.same_primitive_type(value)
            if not primitive._complex:
                return f'repeated {primitive._name}'

        return f'repeated {self.analyze_object_property(key, first, collector, inline_shift)}'

    def analyze_property(self, key: str, value: Any, collector: Collector, inline_shift: str) -> str:
        if isinstance(value, list):
            return self.analyze_array_property(key, value, collector, inline_shift)

        return self.analyze_object_property(key, value, collector, inline_shift)

    def analyze_object_property(self, key: str, value: Any, collector: Collector, inline_shift: str):
        type_name = self.analyze_type(value, collector)

        if type_name == "object":
            message_name = collector.generate_unique_name(to_message_name(key))
            self.add_nested(collector, message_name, value, inline_shift)

            return message_name

        return type_name

    def _test(self, value, regex):
        match = re.match(regex, value)
        return match

    def analyze_type(self, value: Any, collector: Collector) -> str:
        if isinstance(value, str):
            if self.options._google_proto_timestamp and self._test(value, r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+\d\d:\d\d|Z)'):
                collector.add_import(google_timestamp_import)
                return google_timestamp
            else:
                return "string"
        elif isinstance(value, float) or isinstance(value, int):
            return number_type(value)
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, Dict):
            if value is None:
                collector.add_import(google_any_import)
                return google_any

            return "object"

        collector.add_import(google_any_import)

        return google_any;

    def to_primitve_type(self, value: Any) -> ProtoPrimitiveType:
        if isinstance(value, str):
            if self.options._google_proto_timestamp and self._test(value, r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+\d\d:\d\d|Z)'):
                return timestamp_proto_type
            else:
                return string_proto_primitive_type
        elif isinstance(value, float) or isinstance(value, int):
            return ProtoPrimitiveType(number_type(value), False, True)
        elif isinstance(value, bool):
            return bool_proto_primitive_type

        return complex_proto_type;

    def same_primitive_type(self, array: List[Any]) -> ProtoPrimitiveType:
        current = self.to_primitve_type(array[0])
        if current._complex:
            return current

        for item in array:
            next_prim = self.to_primitve_type(item)

            if next_prim._complex:
                return next_prim

            current = merge_primitive_type(current, next_prim)

            if current._complex:
                return current

        return current;

    def add_nested(self, collector: Collector, message_name: str, source: Dict, inline_shift: str):
        lines = []

        lines.append(f'{inline_shift}message {message_name} {{')
        index = 1

        for key, value in source.items():
            type_name = self.analyze_property(key, value, collector, inline_shift)

            lines.append(f'{inline_shift}    {type_name} {key} = {index};')

            index += 1

        lines.append(f'{inline_shift}}}')
        collector.add_message(lines)

    def add_shift(self):
        if self.options._inline:
            return '    '

        return ''


def convert(source: str, options: Options) -> Result:
    if source == '':
        return Result("", "")

    # TODO(bgarrard): This is regex, and needs to be captured
    text = source.replace(r'\.0/g', ".1")

    try:
        json_dict = json.loads(text)
        analyzer = Analyzer(options)
        res = Result(analyzer.analyze(json_dict), "")
        return res
    except Exception as e:
        print("error occurred")
        return Result("", str(e))

def to_message_name(source: str) -> str:
    return source[0].upper() +  source[1:].lower()


def render(imports: Set[str], messages: List[List[str]], lines: List[str], options: Options) -> str:
    result = []
    result.append(f'syntax = "proto3";')

    if len(imports) > 0:
        result.append("")

        for import_name in imports:
            result.append(f'import "{import_name}"')


    result.append("")

    if options._inline:
        result.append("message SomeMessage {")
        if len(messages) > 0:
            result.append("")

            for msg in messages:
                # TODO(bgarrard): Might be wrong
                result.extend(msg)
                result.append("")

        # TODO(bgarrard): Might be wrong
        result.append(*lines)
        result.append("}")
    else:
        for msg in messages:
            result.extend(msg)
            result.append("")

        result.append("message SomeMessage {");
        # TODO(bgarrard): Might be wrong
        result.extend(lines);
        result.append("}");

    return "\n".join(result)

def merge_primitive_type(a: ProtoPrimitiveType, b: ProtoPrimitiveType) -> ProtoPrimitiveType:
    if a._name == b._name:
        return a

    if a._merge and b._merge:
        if a._name == "double":
            return a

        if b._name == "double":
            return b

        if a._name == "int64":
            return a


        if b._name == "int64":
            return b


        if a._name == "uint64":
            if b._name == "uint32":
                return a

        elif b._name == "uint64":
            if a._name == "uint32":
                return b


        return int64_proto_primitive_type

    return complex_proto_type;

def number_type(value: float) -> str:

    if value % 1 == 0:

        if value < 0:
            if value < -2147483648:
                return "int64"

            return "int32";

        if value > 4294967295:
            return "uint64";

        return "uint32"

    return "double"