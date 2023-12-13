class BomCache:
    """
    Class representing a cache holding the current BOM, to be used from other modules

    @author Adrian
    """
    bom = None

    @classmethod
    def get_bom(cls):
        return cls.bom

    @classmethod
    def add_bom(cls, bom):
        cls.bom = bom

    @classmethod
    def reset(cls):
        cls.bom = None
