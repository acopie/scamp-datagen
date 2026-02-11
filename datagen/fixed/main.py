import os
import shutil
import random
import logging
from pathlib import Path
from datetime import datetime

from anytree import Node, RenderTree, Resolver

from datagen.common.utility import check_and_create_if_not_exists, get_abs_file_path
from datagen.common.sequencer import Sequencer
from datagen.common.rootprod import RootProduct, RootNode
from datagen.common.stocks import Stocks

from datagen.multi.quantity import Quantity
from datagen.multi.metainfo import MetaInfo
from datagen.multi.serproduct import SerializableProductDecoder
from datagen.multi.prodmachine import ProdMachines, ProdMachinesAll
from datagen.multi.root_dir import RootDir

from datagen.fixed.decoder import FixedNodesBomDecoder, FixedNodesBoms
from datagen.fixed.gentree import (
    create_tree_fixed_nodes,
    save_fixed_outputs,
)

log = logging.getLogger("main")


def _resolve_abs_or_rel(base: str, default_prefix: str) -> str:
    if os.path.isabs(base):
        return base
    norm = base.replace("\\", "/")
    if norm.startswith(default_prefix + "/"):
        return get_abs_file_path(norm)
    return get_abs_file_path(f"{default_prefix}/{norm}")


def _prepare_products(fixed_bom):
    root_dir_rel = fixed_bom.machines_info.root_directory
    multiboms_target_dir = _resolve_abs_or_rel(root_dir_rel, "multiboms")
    check_and_create_if_not_exists(multiboms_target_dir)

    dst_products = os.path.join(multiboms_target_dir, "rand_products.json")

    src = fixed_bom.products_source
    if not src:
        raise ValueError("products_source is empty in config.")

    src_abs = src if os.path.isabs(src) else get_abs_file_path(src)
    if not os.path.isfile(src_abs):
        raise FileNotFoundError(f"products_source not found: {src_abs}")

    shutil.copyfile(src_abs, dst_products)

    decoder = SerializableProductDecoder(fixed_bom)
    products = decoder.decode(products_path=str(Path(src_abs)))

    if not products:
        raise RuntimeError("No products available to build the tree.")

    # === DEBUG INFO ===
    log.info(f"[DEBUG] Am citit produsele de la calea: {src_abs}")
    log.info(f"[DEBUG] Număr produse: {len(products)}")
    # convertim primele 2 în dict pentru afisare
    preview = []
    for p in products[:2]:
        preview.append({
            "pid": p.pid,
            "code": p.code,
            "pname": p.pname,
            "machines": p.machines
        })
    log.info(f"[DEBUG] Primele 2 produse: {preview}")
    # ==================

    return products


def _compute_output_dir(fixed_bom) -> str:
    out_root = fixed_bom.output_root
    if os.path.isabs(out_root):
        return out_root
    norm = out_root.replace("\\", "/")
    if norm.startswith("boms/"):
        return get_abs_file_path(norm)
    return get_abs_file_path(f"boms/{norm}")


def _build_one_tree(fixed_bom, products, output_dir, output_file_base, shape: str, n_nodes: int, idx: int):
    Sequencer().reset()
    MetaInfo().reset_machines()
    MetaInfo().reset_operations()
    Stocks().reset()
    ProdMachinesAll.reset()
    RootProduct.reset()
    RootNode().reset()

    root_product = random.choice(products)
    if not hasattr(root_product, "operations"):
        root_product.operations = []

    root_operation = Sequencer().index
    root_product.operations.append(root_operation)
    MetaInfo().add_metainfo(root_product, root_operation)
    ProdMachinesAll.add(ProdMachines(getattr(root_product, "pid", getattr(root_product, "productid", 0)),
                                     root_product.machines))

    root = Node(
        "root",
        parent=None,
        operationid=root_operation,
        productid=getattr(root_product, "pid", getattr(root_product, "productid", 0)),
        code=root_product.code,
        pname=root_product.code,
        parentid=None,
        start_date=fixed_bom.machines_info.start_date,
        delivery_date=fixed_bom.machines_info.start_date,
        priority=random.randint(1, 10),
        quantity=Quantity.get_quantity(
            fixed_bom.products_info[0].quantity.min,
            fixed_bom.products_info[0].quantity.step,
            fixed_bom.products_info[0].quantity.max,
        ),
    )
    RootNode().add_node(root)
    RootProduct.add_root(root_product)

    create_tree_fixed_nodes(
        root=root,
        products=products,
        n_total=n_nodes,
        shape=shape,
        rng=random.Random(),
    )

    out_name = f"{os.path.splitext(output_file_base)[0]}_{idx}.json"
    json_path, tree_path = save_fixed_outputs(root, output_dir, out_name)

    log.info(f"[fixed] Exported JSON: {json_path}")
    log.info(f"[fixed] Exported TREE: {tree_path}")


def _create_run_folder(base_output_dir: str) -> str:
    """
    Creeaza un subdirector unic pentru rulara curenta sub base_output_dir
    """
    check_and_create_if_not_exists(base_output_dir)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = os.path.join(base_output_dir, f"run_{ts}")

    if not os.path.exists(candidate):
        os.makedirs(candidate, exist_ok=True)
        return candidate

    i = 1
    while True:
        cand = f"{candidate}_{i:02d}"
        if not os.path.exists(cand):
            os.makedirs(cand, exist_ok=True)
            return cand
        i += 1

def start_fixed(configuration_file_path: str) -> None:
    if not configuration_file_path:
        raise SystemExit("Missing -c/--configFilePath for fixed mode.")

    FixedNodesBomDecoder.build(configuration_file_path)
    all_boms = FixedNodesBoms.get_all()
    if not all_boms:
        raise SystemExit("No fixed-nodes BOMs found in configuration.")

    for fixed_bom in all_boms:
        products = _prepare_products(fixed_bom)
        # directorul baza din config (poate fi absolut, 'boms/...', sau simplu)
        base_output_dir = _compute_output_dir(fixed_bom)

        # creeaza subfolder pentru rularea curenta
        run_output_dir = _create_run_folder(base_output_dir)
        log.info(f"[fixed] Run output dir: {run_output_dir}")

        # setul pentru unicitate, resetat pe fiecare rulare a acestui fixed_bom
        shape_sigs = set()

        for prod_info in fixed_bom.products_info:
            base_name = prod_info.output_file

            for idx in range(1, fixed_bom.k_trees + 1):
                _build_one_tree(
                    fixed_bom=fixed_bom,
                    products=products,
                    output_dir=run_output_dir,   
                    output_file_base=base_name,
                    shape=fixed_bom.shape,
                    n_nodes=fixed_bom.n_nodes,
                    idx=idx,
                )
