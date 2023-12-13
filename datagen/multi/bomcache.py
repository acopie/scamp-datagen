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


class MultiBomCache:
    """
    Class representing a cache holding the current MultiBOM representation, to be used from other modules
    """
    multi_bom = None

    @classmethod
    def get_bom(cls):
        return cls.multi_bom

    @classmethod
    def add_bom(cls, multi_bom):
        cls.multi_bom = multi_bom

    @classmethod
    def reset(cls):
        cls.multi_bom = None
