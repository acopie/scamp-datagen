"""
Generator pentru 'bounded' (min/max copii per nod) + completări verticale ca exceptie.
algoritm:
 - Faza A: crestere n-ary iterativa, respectand [min_children, max_children] per nod extins
 - Faza B: daca ramane 'remaining' > 0 și nu mai putem progresa în Faza A,
           completam cu lanturi verticale (1 copil/nod), ignorand DOAR regula 'min_children
"""
from __future__ import annotations
import logging, random
from typing import List, Optional, Dict, Tuple
from anytree import AnyNode, PreOrderIter

# refolosim utilitare de export/afișare din multi
from datagen.multi.gentree import (
    export_tree,
    import_tree,
    render_tree,
    simple_render_tree,
)

from datagen.common.sequencer import Sequencer
from datagen.multi.metainfo import MetaInfo
from datagen.multi.prodmachine import ProdMachines, ProdMachinesAll
from datagen.multi.quantity import Quantity
from datagen.common.rootprod import RootProduct
from datagen.multi.root_dir import RootDir

log = logging.getLogger("main")


class InsufficientProductsError(Exception):
    pass


# ------------- helperi eligibilitate / atasare -------------
def _pid(prod) -> int:
    return getattr(prod, "pid", getattr(prod, "productid", 0))

def _code(prod) -> str:
    return getattr(prod, "code", getattr(prod, "pname", ""))

def _path_product_ids(leaf) -> set[int]:
    s = set()
    n = leaf
    while n is not None:
        pid = getattr(n, "productid", None)
        if pid is not None:
            s.add(pid)
        n = n.parent
    return s

def _leaves_of(root) -> List:
    return [n for n in PreOrderIter(root) if len(getattr(n, "children", [])) == 0]

def _current_children_count(node) -> int:
    return len(getattr(node, "children", []))

def _eligible_capacity_for_leaf(leaf, products_count: int, max_children: int) -> int:
    """
    Capacitate maxima de noi copii pe frunza, tinand cont de:
      - limita max_children per nod
      - produse distincte deja pe calea root->leaf
    """
    by_max = max(0, max_children - _current_children_count(leaf))
    used_on_path = len(_path_product_ids(leaf))
    by_products = max(0, products_count - used_on_path)
    return min(by_max, by_products)

def _pick_product_for_leaf(leaf, products: List, rng: random.Random):
    """Alege un produs cu id unic  pe calea root->leaf"""
    used = _path_product_ids(leaf)
    tries = min(5 * len(products), 2000)
    for _ in range(tries):
        p = rng.choice(products)
        if _pid(p) not in used:
            return p
    return None

def _attach_child(parent, product, qty_triplet: Tuple[int, int, int]):
    opid = Sequencer().index
    MetaInfo().add_metainfo(product, opid)
    ProdMachinesAll.add(ProdMachines(_pid(product), getattr(product, "machines", [])))

    qmin, qstep, qmax = qty_triplet
    qty = Quantity.get_quantity(qmin, qstep, qmax)

    child = AnyNode(
        parent=parent,
        parentid=getattr(parent, "operationid", None),
        operationid=opid,
        productid=_pid(product),
        code=_code(product),
        pname=_code(product),
        quantity=qty,
        machines=getattr(product, "machines", []),
    )
    return child


# ------------- generator principal -------------
def create_tree_bounded(
    *,
    root,
    products: List,
    n_total: int,
    min_children: int,
    max_children: int,
    rng: random.Random,
    qty_triplet: Tuple[int, int, int],
    vertical_cfg: Optional[dict] = None,
) -> None:

    assert n_total >= 1, "n_total trebuie sa fie >= 1"
    products_count = len(products)
    remaining = n_total - 1  # root deja exista

    # ---- Faza A: n-ary controlat de [min_children, max_children]
    while remaining > 0:
        leaves = _leaves_of(root)

        # frunze capabile sa primeasca cel putin min_children copii acum
        elig = []
        for lf in leaves:
            cap = _eligible_capacity_for_leaf(lf, products_count, max_children)
            if cap >= min_children:
                elig.append((lf, cap))

        if not elig:
            break  # nu mai putem asigura minimul => trecem la verticale

        Lmax = remaining // min_children
        if Lmax <= 0:
            break

        rng.shuffle(elig)
        leaves_sel = [lf for (lf, cap) in elig[: min(len(elig), Lmax)]]

        # alocare minim
        alloc: Dict[object, int] = {lf: min_children for lf in leaves_sel}
        remaining_after_min = remaining - len(leaves_sel) * min_children
        if remaining_after_min < 0:
            remaining_after_min = 0

        # extra - peste minim
        extras: Dict[object, int] = {}
        total_extra_cap = 0
        for lf in leaves_sel:
            cap_now = _eligible_capacity_for_leaf(lf, products_count, max_children)
            ex = max(0, cap_now - min_children)
            extras[lf] = ex
            total_extra_cap += ex

        budget = min(remaining_after_min, total_extra_cap)

        # distribuire round-robin aleator
        order = leaves_sel[:]
        rng.shuffle(order)
        i = 0
        while budget > 0 and any(v > 0 for v in extras.values()):
            lf = order[i % len(order)]
            if extras[lf] > 0:
                alloc[lf] += 1
                extras[lf] -= 1
                budget -= 1
            i += 1

        # atasam conform alocarilor
        added = 0
        for lf, c_i in alloc.items():
            for _ in range(c_i):
                prod = _pick_product_for_leaf(lf, products, rng)
                if not prod:
                    continue
                _attach_child(lf, prod, qty_triplet)
                remaining -= 1
                added += 1
                if remaining == 0:
                    break
            if remaining == 0:
                break

        if added == 0:
            break  # nu am reusit sa adaugam nimic în pasul asta; trecem la verticale

    # ---- Faza B: verticale 
    if remaining > 0:
        vcfg = vertical_cfg or {}
        if not vcfg.get("enabled", True):
            raise InsufficientProductsError(
                f"[bounded] Nu putem atinge n_total={n_total}. remaining={remaining}; verticale dezactivate."
            )

        min_d = int(vcfg.get("min_depth", 1))
        max_d = int(vcfg.get("max_depth", 1))
        if min_d < 1:
            min_d = 1
        if max_d < 1:
            max_d = 1
        if max_d < min_d:
            max_d = min_d

        attempts = 0
        max_attempts = 5 * remaining  # limita de incercari 
        while remaining > 0 and attempts < max_attempts:
            # frunze care pot primi inca 1 copil (respecta max_children si eligibilitatea)
            starts = []
            for lf in _leaves_of(root):
                if _eligible_capacity_for_leaf(lf, products_count, max_children) >= 1:
                    starts.append(lf)
            if not starts:
                break

            start = rng.choice(starts)
            chain_len = min(remaining, rng.randint(min_d, max_d))

            curr = start
            steps = 0
            while steps < chain_len and remaining > 0:
                # verifica capacitatea pentru nodul curent (start sau copilul abia creat)
                if _eligible_capacity_for_leaf(curr, products_count, max_children) < 1:
                    break
                prod = _pick_product_for_leaf(curr, products, rng)
                if not prod:
                    break
                child = _attach_child(curr, prod, qty_triplet)
                remaining -= 1
                steps += 1
                curr = child  # lantul in jos

            attempts += 1

        if remaining > 0:
            raise InsufficientProductsError(
                f"[bounded] Nu exista capacitate pentru completari verticale. remaining={remaining}."
            )
