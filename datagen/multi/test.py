import json

def exclude_from_serialization(func):
    func.exclude_from_serialization = True
    return func

class MyClass:
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3

    @exclude_from_serialization
    def field2(self):
        return self.field2

obj = MyClass('val1', 'val2', 'val3')

def custom_dict(obj):
    return {
        key: value for key, value in obj.__dict__.items() if not hasattr(value, 'exclude_from_serialization')
    }

serialized_data = json.dumps(custom_dict(obj), indent=4)
print(serialized_data)