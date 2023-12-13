from typing import Type


class SerializableMachine:
    """
    Class modelling a machine that will be used in the serialization process
    """

    def __init__(self, id: int, name: str, oee: float, setup_time: float, execution_time):
        # the product id
        self.id: int = id
        self.name: str = name
        self.oee: float = oee
        self.setup_time: float = setup_time
        self.execution_time = execution_time

    def __eq__(self, o: Type['SerializableMachine']) -> bool:
        """
        Overrides the default __eq__ method in order to provide uniqueness in collections
        """
        if isinstance(o, SerializableMachine):
            return ((self.name == o.name) and (self.id == o.id) and (self.oee == o.oee) and
                    (self.setup_time == o.setup_time) and (self.execution_time == o.execution_time))
        else:
            return False

    def __hash__(self):
        """
        Overrides the default __hash__ method of the object class, used to define uniqueness in collections
        """
        return hash(self.id, self.name, self.oee, self.execution_time, self.setup_time)
