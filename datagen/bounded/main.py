# datagen/bounded/main.py
"""
Entry-point pentru generatorul 'bounded' (k arbori cu exact n noduri, [min,max] copii/nod)
Reutilizeaza utilitati din 'fixed' pentru cai, produse și salvare
"""
import os, random, logging
from anytree import Node, Resolver, RenderTree

from datagen.common.utility import check_and_create_if_not_exists, get_abs_file_path
from datagen.common.sequencer import Sequencer
from datagen.common.rootprod import RootProduct, RootNode
from datagen.common.stocks import Stocks

from datagen.multi.quantity import Quantity
from datagen.multi.metainfo import MetaInfo
from datagen.multi.prodmachine import ProdMachines, ProdMachinesAll
from datagen.multi.root_dir import RootDir

# Refolosim helperii de path și produse din fixed
from datagen.fixed.main import (
    _resolve_abs_or_rel,
    _prepare_products,
    _compute_output_dir,
    _create_run_folder,
)

# Afisare / export
from datagen.bounded.gentree import create_tree_bounded, InsufficientProductsError
from datagen.multi.gentree import export_tree, import_tree, render_tree
from datagen.fixed.gentree import simple_render_tree

log = logging.getLogger("main")


def _set_rootdir_from_output_dir(output_dir: str) -> None:
    """
    Seteaza RootDir relativ sub 'boms/' astfel incat simple_render_tree sa scrie langa JSON.
    """
    abs_boms = get_abs_file_path("boms").replace("\\", "/")
    out_dir_norm = output_dir.replace("\\", "/")
    if out_dir_norm.startswith(abs_boms + "/"):
        rel_under_boms = out_dir_norm[len(abs_boms) + 1 :]
        RootDir().set(rel_under_boms)
    else:
        RootDir().set(".")


def _build_one_tree(bom, products, output_dir, output_file_base, idx: int):
    # reset state comun
    Sequencer().reset()
    MetaInfo().reset_machines()
    MetaInfo().reset_operations()
    Stocks().reset()
    ProdMachinesAll.reset()
    RootProduct.reset()
    RootNode().reset()

    # root product
    root_product = random.choice(products)
    if not hasattr(root_product, "operations"):
        root_product.operations = []

    root_operation = Sequencer().index
    root_product.operations.append(root_operation)
    MetaInfo().add_metainfo(root_product, root_operation)
    ProdMachinesAll.add(ProdMachines(getattr(root_product, "pid", getattr(root_product, "productid", 0)),
                                     getattr(root_product, "machines", [])))

    root = Node(
        "root",
        parent=None,
        operationid=root_operation,
        productid=getattr(root_product, "pid", getattr(root_product, "productid", 0)),
        code=getattr(root_product, "code", getattr(root_product, "pname", "")),
        pname=getattr(root_product, "code", getattr(root_product, "pname", "")),
        parentid=None,
        start_date=bom.machines_info.start_date,
        delivery_date=bom.machines_info.start_date,  # dummy ok
        priority=random.randint(1, 10),
        quantity=Quantity.get_quantity(
            bom.products_info[0].quantity.min,
            bom.products_info[0].quantity.step,
            bom.products_info[0].quantity.max,
        ),
    )
    RootNode().add_node(root)
    RootProduct.add_root(root_product)

    # generare structura
    qty_triplet = (
        bom.products_info[0].quantity.min,
        bom.products_info[0].quantity.step,
        bom.products_info[0].quantity.max,
    )

    rng = random.Random()
    try:
        create_tree_bounded(
            root=root,
            products=products,
            n_total=bom.n_nodes,
            min_children=bom.min_children,
            max_children=bom.max_children,
            rng=rng,
            qty_triplet=qty_triplet,
            vertical_cfg=bom.vertical_tree,
        )
    except InsufficientProductsError as e:
        log.warning(str(e))
        return

    # atasare operations_list si salvam
    resolver = Resolver("name")
    root_node = resolver.get(root, "/root")
    root_node.operations_list = MetaInfo().get_operations()

    check_and_create_if_not_exists(output_dir)
    out_name = f"{os.path.splitext(output_file_base)[0]}_{idx}.json"
    out_path = os.path.join(output_dir, out_name)

    export_tree(root, out_path, False)
    try:
        node = import_tree(out_path)
        render_tree(node)
    except Exception:
        pass

    _set_rootdir_from_output_dir(output_dir)
    simple_render_tree(root_node, os.path.splitext(out_name)[0])

    log.info(f"[bounded] Exported: {out_path}")


def start_bounded(configuration_file_path: str) -> None:
    if not configuration_file_path:
        raise SystemExit("Missing -c/--configFilePath for bounded mode.")

  
    from datagen.bounded.decoder import BoundedBomDecoder, BoundedBoms

    BoundedBomDecoder.build(configuration_file_path)
    all_boms = BoundedBoms.get_all()
    if not all_boms:
        raise SystemExit("No bounded BOMs found in configuration.")

    for bom in all_boms:
        # pregateste produsele la locul standard (multiboms/<root_dir>/rand_products.json)
        products = _prepare_products(bom)

        # calculeaza directorul de iesire + subfolder de rulare
        base_output_dir = _compute_output_dir(bom)
        run_output_dir = _create_run_folder(base_output_dir)
        log.info(f"[bounded] Run output dir: {run_output_dir}")

        for prod_info in bom.products_info:
            base_name = prod_info.output_file
            for idx in range(1, bom.k_trees + 1):
                _build_one_tree(
                    bom=bom,
                    products=products,
                    output_dir=run_output_dir,
                    output_file_base=base_name,
                    idx=idx,
                )
