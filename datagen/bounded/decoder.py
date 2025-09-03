import logging
from json import load, JSONDecoder

from datagen.common.utility import get_abs_file_path

from datagen.multi.prodinfo import ProductInfo
from datagen.multi.machineinfo import (
    MachineInfo,
    UnitAssemblyTime,
    SetupTime,
    MaintenanceDuration,
    MaintenanceInterval,
    OEE,
)

log = logging.getLogger("main")


class BoundedBom:
    def __init__(
        self,
        *,
        products_info,
        machines_info,
        n_nodes: int,
        k_trees: int,
        min_children: int,
        max_children: int,
        vertical_tree: dict | None,
        root_directory: str,
        products_source: str,
        output_root: str,
    ):
        self.products_info = products_info
        self.machines_info = machines_info
        self.n_nodes = n_nodes
        self.k_trees = k_trees
        self.min_children = min_children
        self.max_children = max_children
        self.vertical_tree = vertical_tree or {"enabled": False}
        self.root_directory = root_directory
        self.products_source = products_source
        self.output_root = output_root


class BoundedBoms:
    _instance = None
    _boms = []

    def __new__(cls, *a, **k):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def add_bom(cls, bom: BoundedBom) -> None:
        cls._boms.append(bom)

    @classmethod
    def get_all(cls):
        return cls._boms


class BoundedBomDecoder(JSONDecoder):
    @classmethod
    def _product_info_from_entry(cls, entry: dict) -> ProductInfo:
        name = entry.get("name", "BOM_Bounded")
        output_file = entry.get("output_file", "bom_bounded.json")
        quantity = entry.get("quantity", {"min": 1, "step": 1, "max": 1})

        return ProductInfo(
            name=name,
            output_file=output_file,
            max_depth=10**9,              # nefolosit aici
            max_children=10**9,           # nefolosit aici
            randomize_children=False,
            delivery_date=entry.get("delivery_date", "2099-12-31 00:00:00.000000"),
            quantity=quantity,
            vertical_tree_depth={"min": 0, "step": 1, "max": 0, "probability": 0.0},
        )

    @classmethod
    def _machine_info_from_block(cls, m: dict, root_directory: str) -> MachineInfo:
        return MachineInfo(
            start_date=m["start_date"],
            prod_number=m["prod_number"],
            root_directory=root_directory,
            machines_number=m["machines_number"],
            max_alternatives_machines_number=m["max_alternatives_machines_number"],
            randomize_alternative_machines=m["randomize_alternative_machines"],
            allow_identical_machines=m["allow_identical_machines"],
            percent_of_identical_machines=m["percent_of_identical_machines"],
            unit_assembly_time=UnitAssemblyTime(**m["unit_assembly_time"]),
            maintenance_duration=MaintenanceDuration(**m["maintenance_duration"]),
            maintenance_interval=MaintenanceInterval(**m["maintenance_interval"]),
            maintenance_probability=m["maintenance_probability"],
            oee=OEE(**m["oee"]),
            setup_time=SetupTime(**m["setup_time"]),
        )

    @classmethod
    def decode(cls, todecode: dict):
        items = todecode.get("boms_bounded_children", [])
        for b in items:
            outputs = b.get("outputs", [])
            n_nodes = b.get("n_nodes")
            k_trees = b.get("k_trees")
            min_children = int(b.get("min_children", 1))
            max_children = int(b.get("max_children", 1))
            vertical_tree = b.get("vertical_tree", {"enabled": False})

            root_directory = b.get("root_directory", "bounded_products")
            products_source = b.get("products_source")
            output_root = b.get("output_root", "bounded_output")

            if n_nodes is None or k_trees is None:
                log.error("Missing required keys 'n_nodes' or 'k_trees' in bounded config entry.")
                continue
            if products_source is None:
                log.error("Missing 'products_source' in bounded config entry.")
                continue
            if min_children < 0 or max_children < 0 or min_children > max_children:
                log.error(f"Invalid children bounds: min={min_children}, max={max_children}.")
                continue

            products_info = [cls._product_info_from_entry(e) for e in outputs]
            mblock = b.get("machines_info")
            if not mblock:
                log.error("Missing 'machines_info' block in bounded config entry.")
                continue

            machines_info = cls._machine_info_from_block(mblock, root_directory)

            BoundedBoms.add_bom(
                BoundedBom(
                    products_info=products_info,
                    machines_info=machines_info,
                    n_nodes=int(n_nodes),
                    k_trees=int(k_trees),
                    min_children=min_children,
                    max_children=max_children,
                    vertical_tree=vertical_tree,
                    root_directory=root_directory,
                    products_source=products_source,
                    output_root=output_root,
                )
            )
        return BoundedBoms.get_all()

    @classmethod
    def build(cls, configuration_file_path: str):
        log.info("Importing bounded-children BOM config file...")
        with open(get_abs_file_path(configuration_file_path), "r", encoding="utf-8") as f:
            data = load(f)
            return cls.decode(data)