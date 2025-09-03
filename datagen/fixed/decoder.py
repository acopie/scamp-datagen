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


class FixedNodesBom:
    def __init__(
        self,
        products_info,
        machines_info,
        n_nodes: int,
        k_trees: int,
        shape: str,
        root_directory: str,   # relativ pentru multiboms/<root_directory>
        products_source: str,  # cale catre produses
        output_root: str       # locul pt salvare rezulate
    ):
        self.products_info = products_info
        self.machines_info = machines_info
        self.n_nodes = n_nodes
        self.k_trees = k_trees
        self.shape = shape
        self.root_directory = root_directory
        self.products_source = products_source
        self.output_root = output_root


class FixedNodesBoms:
    _instance = None
    _fixed_boms = []

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def add_fixed_bom(cls, bom: FixedNodesBom) -> None:
        cls._fixed_boms.append(bom)

    @classmethod
    def get_all(cls):
        return cls._fixed_boms


class FixedNodesBomDecoder(JSONDecoder):
    @classmethod
    def _product_info_from_entry(cls, entry: dict, n_nodes: int) -> ProductInfo:
        name = entry.get("name", "BOM_Fixed")
        output_file = entry.get("output_file", "bom_fixed_nodes.json")
        quantity = entry.get("quantity", {"min": 1, "step": 1, "max": 1})

        return ProductInfo(
            name=name,
            output_file=output_file,
            max_depth=10**9,                # nefolosit în fixed
            max_children=max(1, n_nodes),   # nefolosit în fixed
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
        items = todecode.get("boms_fixed_nodes", [])
        for b in items:
            outputs = b.get("outputs", [])
            n_nodes = b.get("n_nodes")
            k_trees = b.get("k_trees")
            shape = b.get("shape", "random")
            root_directory = b.get("root_directory", "fixed_products")  # relativ pt multiboms
            products_source = b.get("products_source")
            output_root = b.get("output_root", "fixed_output")          # în boms/

            if n_nodes is None or k_trees is None:
                log.error("Missing required keys 'n_nodes' or 'k_trees' in fixed config entry.")
                continue
            if not products_source:
                log.error("Missing 'products_source' in fixed config entry.")
                continue

            products_info = [cls._product_info_from_entry(entry, n_nodes) for entry in outputs]

            mblock = b.get("machines_info")
            if not mblock:
                log.error("Missing 'machines_info' block in fixed config entry.")
                continue

            machines_info = cls._machine_info_from_block(mblock, root_directory)

            FixedNodesBoms.add_fixed_bom(
                FixedNodesBom(
                    products_info=products_info,
                    machines_info=machines_info,
                    n_nodes=n_nodes,
                    k_trees=k_trees,
                    shape=shape,
                    root_directory=root_directory,
                    products_source=products_source,
                    output_root=output_root,
                )
            )

        return FixedNodesBoms.get_all()

    @classmethod
    def build(cls, configuration_file_path: str):
        log.info("Importing fixed-nodes BOM config file...")
        try:
            with open(get_abs_file_path(configuration_file_path), "r", encoding="utf-8") as f:
                data = load(f)
                return cls.decode(data)
        except FileNotFoundError:
            log.error(f"Config file {configuration_file_path} not found.")
            raise
