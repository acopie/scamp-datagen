class Sequencer(object):
    """
    Singleton class to generate unique ids for the data generator

    @author Adrian
    """

    # this will hold the current sequence
    index = 0

    _instance: object = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> int:
        self.id = Sequencer.index
        Sequencer.index += 1

    def reset(self) -> None:
        """
        Resets the sequencer
        :return: None
        """
        Sequencer.index = 0
