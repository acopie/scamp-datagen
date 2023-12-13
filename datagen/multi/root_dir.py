class RootDir(object):
    """
    Singleton class holding the root directory of a multi-bom configuration

    @author Adrian
    """

    # this will hold the root directory for a multi-bom configuration
    root_dir = ""

    _instance: object = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set(self, root_dir):
        RootDir.root_dir = root_dir

    def get(self):
        return self.root_dir

    def reset(self) -> None:
        """
        Resets the root_dir variable
        :return: None
        """
        RootDir.root_dir = ""
