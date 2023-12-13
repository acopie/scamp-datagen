class MachineSequencer(object):
    """
    Singleton class to generate unique ids for the machines in data generator
    """

    # this will hold the current sequence
    index = 0

    _instance: object = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.id = MachineSequencer.index
        MachineSequencer.index += 1

    @classmethod
    def reset(cls) -> None:
        """
        Resets the sequencer
        :return:
        """
        MachineSequencer.index = 1
