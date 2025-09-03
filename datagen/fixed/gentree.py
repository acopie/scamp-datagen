"""
Generator pentru 'fixed' - fara restrictionari legate de numarul de copii per nod sau legate de adancime
algoritm:   alegerea aleatoare din frontiera a unui numar de frunze care sa aibă copii, identificarea acelor 
frunze si pentru fiecare alegerea numarului de copii
            alegerile sunt influentate de forma arborelui- am definit 3 forme: adânc, lat și balansat
"""

import os
import math
import logging
import random
from typing import List, Tuple

from anytree import AnyNode, RenderTree, PreOrderIter

from datagen.multi.gentree import (
    export_tree,
    import_tree,
    render_tree,
)
from datagen.multi.root_dir import RootDir
from datagen.common.utility import get_abs_file_path, check_and_create_if_not_exists

from datagen.common.sequencer import Sequencer
from datagen.multi.metainfo import MetaInfo
from datagen.multi.prodmachine import ProdMachines, ProdMachinesAll
from datagen.multi.quantity import Quantity

log = logging.getLogger("main")


# ---------- .tree writer (boms/...) ----------
def simple_render_tree(root_node, output_file_base: str) -> None:
    """
    scrie fisierul .tree in boms/<RootDir().get()>/<output_file_base>.tree
    """
    rel_under_boms = RootDir().get().replace("\\", "/")
    boms_target_dir = get_abs_file_path(f"boms/{rel_under_boms}")
    check_and_create_if_not_exists(boms_target_dir)

    out_path = os.path.join(boms_target_dir, f"{output_file_base}.tree")
    print(f"config_path {out_path}")

    with open(out_path, "w", encoding="utf-8") as f:
        for pre, _, node in RenderTree(root_node):
            label = getattr(node, "pname", getattr(node, "name", ""))
            f.write(f"{pre}{label}\n")


# ---------- Utilitare pentru frontiera ----------
def _leaves_of(root) -> List:
    """ Returneaza toate frunzele unei radacini date"""
    return [n for n in PreOrderIter(root) if len(getattr(n, "children", [])) == 0]


def _deepest_leaf(leaves: List) -> object:
    """Alege o frunză cu adâncime maxima, iar daca sunt mai multe, una aleatoare dintre ele"""
    if not leaves:
        return None
    max_depth = max(l.depth for l in leaves)
    candidates = [l for l in leaves if l.depth == max_depth]
    return random.choice(candidates)



def _sample_int_biased_low(rng, lo: int, hi: int, p_single: float = 0.65) -> int:
    """
    alegere numar din interval
    cu probabilitate p_single întoarce 'lo'; altfel uniform în [lo, hi]
    """
    if lo >= hi:
        return lo
    if rng.random() < p_single:
        return lo
    return rng.randint(lo, hi)


def _select_leaves(
    leaves: List,
    shape: str,
    remaining: int,
    rng: random.Random,
    *,
    # parametri pentru variabilitate
    small_max_leaves_deep: int = 3,     # nr maxim de frunze extinse pe iteratie la deep
    min_frac_wide: float = 0.7,         #  probabilitate minima din frunze pe care le extindem la wide
    max_frac_wide: float = 1.0,         # probabilitate maxima din frunze pe care le extindem la wide (toate)
) -> List:
    """
    alege frunzele ce urmeaza sa fie extinse in acesata iteratie, in functie de forma
    - deep: 1..small_max_leaves_deep frunze, alese dintre cele mai adanci (alegere tinde spre 1)
    - wide: 70–100% dintre frunze (random în [min_frac_wide, max_frac_wide]), limitat de 'remaining'
    - balanced:  ~jumatate
    """
    if not leaves or remaining <= 0:
        return []

    if shape == "deep":
        # se obtin frunzele ordonate descrescator dupa adancime
        max_depth = max(l.depth for l in leaves)
        by_depth = {}
        for l in leaves:
            by_depth.setdefault(l.depth, []).append(l)
        depths = sorted(by_depth.keys(), reverse=True)

        # se alege limita L (1..small_max_leaves_deep), bias spre 1 - numarul de frunze care sa aiba copii
        L_cap = min(small_max_leaves_deep, len(leaves), remaining)
        L = _sample_int_biased_low(rng, 1, max(1, L_cap), p_single=0.75)

        # se aleg cele L frunze incepand de la adancimea cea mai mare
        picked = []
        for d in depths:
            rng.shuffle(by_depth[d])
            for lf in by_depth[d]:
                picked.append(lf)
                if len(picked) >= L:
                    break
            if len(picked) >= L:
                break
        return picked

    if shape == "wide":
        # se selecteaza o fractie mare din frunze
        frac = rng.uniform(min_frac_wide, max_frac_wide)
        L = max(1, int(round(frac * len(leaves))))
        L = min(L, len(leaves), remaining)  #tinem cont de cate noduri mai avem de generat
        leaves_cp = list(leaves)
        rng.shuffle(leaves_cp)
        return leaves_cp[:L]

    # balanced- jumatate din frunze vor avea copii
    k = max(1, math.ceil(len(leaves) / 2))
    leaves_cp = list(leaves)
    rng.shuffle(leaves_cp)
    return leaves_cp[:min(k, remaining)]



def _allocate_children(
    leaves_sel: List,
    remaining: int,
    shape: str,
    rng: random.Random,
    *,
    
    small_max_children_deep: int = 3,
    small_max_children_wide: int = 2,
) -> List[int]:
    """
    Returneaza [c_i] pentru fiecare frunza selectata, adica determina pt fiecare frunza nr de copii pe care sa il aiba, 
    in functie de forma
    - deep fiecare frunza primeste 1..small_max_children_deep (bias spre 1)
    - wide fiecare frunza primeste 1..small_max_children_wide (bias spre 1)
    - balanced simplu (toti 1) 
    Daca se depaseste remaining se fac "taieri"
    """
    if not leaves_sel or remaining <= 0:
        return []

    if shape == "deep":
        alloc = [
            _sample_int_biased_low(rng, 1, small_max_children_deep, p_single=0.75)
            for _ in leaves_sel
        ]
    elif shape == "wide":
        alloc = [
            _sample_int_biased_low(rng, 1, small_max_children_wide, p_single=0.7)
            for _ in leaves_sel
        ]
    else:  
        alloc = [1] * len(leaves_sel)

    total = sum(alloc)
    if total <= remaining:
        return alloc

    # Daca s-a dapasit remaining sa fac taieri din alocari
    # pentru wide taiem mai întai de la frunzele cele mai adanci,
    # pentru deep/balanced taiem din spate 
    to_cut = total - remaining
    if shape == "wide":
        # sortam index-urile frunzelor descrescator dupa adancime
        idxs = list(range(len(leaves_sel)))
        idxs.sort(key=lambda i: leaves_sel[i].depth, reverse=True)
    else:
        idxs = list(range(len(leaves_sel)-1, -1, -1))

    for i in idxs:
        if to_cut == 0:
            break
        cut_here = min(alloc[i] - 1, to_cut)  # ramane cel putin 1 copil/frunza
        if cut_here > 0:
            alloc[i] -= cut_here
            to_cut -= cut_here

    # daca tot mai avem de taiat 
    i = 0
    while to_cut > 0 and i < len(alloc):
        if alloc[i] > 0:
            alloc[i] -= 1
            to_cut -= 1
        i += 1

    # OBS: eliminarea frunzelor cu 0 copii se face indirect (in bucla de atașare ignoram c_i <= 0)
    return alloc


# ---------- Validare produse ----------
def _path_pid_set(node) -> set:
    s = set()
    crt = node
    while crt is not None:
        pid = getattr(crt, "productid", None)
        if pid is not None:
            s.add(pid)
        crt = crt.parent
    return s


def _pick_product_for_leaf(leaf, products) -> object:
    #Alege un produs random al carui pid NU este în calea pana la radacina
    used = _path_pid_set(leaf)
    idxs = list(range(len(products)))
    random.shuffle(idxs)
    for i in idxs:
        p = products[i]
        pid = getattr(p, "pid", getattr(p, "productid", None))
        if pid not in used:
            return p
    return None


def _attach_child(parent, product, qty_min_step_max: Tuple[int, int, int]):
    #ataseaza un copil AnyNode si inregistreaza metainfo/machines ca in multi
    qmin, qstep, qmax = qty_min_step_max
    operation_id = Sequencer().index
    MetaInfo().add_metainfo(product, operation_id)
    ProdMachinesAll.add(ProdMachines(getattr(product, "pid", getattr(product, "productid", 0)),
                                     getattr(product, "machines", [])))

    return AnyNode(
        parent=parent,
        parentid=getattr(parent, "operationid", None),
        operationid=operation_id,
        productid=getattr(product, "pid", getattr(product, "productid", 0)),
        code=getattr(product, "code", "CODE"),
        pname=getattr(product, "code", "CODE"),
        quantity=Quantity.get_quantity(qmin, qstep, qmax),
        machines=getattr(product, "machines", []),
    )


# ---------- Generatorul propriu-zis ----------
def create_tree_fixed_nodes(
    root,
    products,
    n_total: int,
    shape: str,           # "deep"/"wide"/"balanced" 
    rng: random.Random,  
    max_children=None,    #lipsa
):
    """
    Construieste un arbore cu exact n_total noduri pe baza formelor simple
    """
    count_nodes = 1
    if n_total <= 1:
        return


    while count_nodes < n_total:
        remaining = n_total - count_nodes
        leaves = _leaves_of(root)

        leaves_sel = _select_leaves(leaves, shape, remaining, rng)
        if not leaves_sel:
            if leaves:
                leaves_sel = [rng.choice(leaves)]
            else:
                break

        alloc = _allocate_children(leaves_sel, remaining, shape, rng)
        if sum(alloc) == 0:
            break


        added = 0
        for lf, c_i in zip(leaves_sel, alloc):
            if c_i <= 0:
                continue
            for _ in range(c_i):
                prod = _pick_product_for_leaf(lf, products)
                if not prod:
                    # daca nu gasim produs eligibil pe frunza asta, trecem mai departe
                    continue
                _attach_child(
                    lf,
                    prod,
                    (1, 1, 1)  #  copiii pot fi 1, pt radacina din config
                )
                count_nodes += 1
                added += 1
                if count_nodes >= n_total:
                    break
            if count_nodes >= n_total:
                break

        if added == 0:
            # nu am reusit sa adaugam nimic -> nu blocam
            break


# --- Salvare rezultate (JSON + .tree) ---

import os
from anytree import Resolver
from datagen.common.utility import get_abs_file_path, check_and_create_if_not_exists
from datagen.multi.root_dir import RootDir
from datagen.multi.metainfo import MetaInfo

def _set_rootdir_from_output_dir(output_dir: str) -> None:
    """
    Seteaza RootDir ca subfolder relativ sub 'boms/', astfel incat .tree să fie salvat
    în acelasi loc cu JSON-urile.
    """
    abs_boms = get_abs_file_path("boms").replace("\\", "/")
    out_dir_norm = output_dir.replace("\\", "/")
    if out_dir_norm.startswith(abs_boms + "/"):
        rel_under_boms = out_dir_norm[len(abs_boms) + 1:]
        RootDir().set(rel_under_boms)
    else:
        RootDir().set(".")

def save_fixed_outputs(root, output_dir: str, output_file: str) -> tuple[str, str]:
    """
    Salveaza arborele in:
      - JSON: <output_dir>/<output_file>
      - .tree: boms/<RootDir().get()>/<basename>.tree 
    Se poate face o mica modificare pentru ca formatula din terminal cu continutul .tree sa fie identic
    Acum salvat este formatul compactat, iar printul este detaliat
    """
    # 1) atasare operations_list pe radacina (ca în multi)
    resolver = Resolver('name')
    root_node = resolver.get(root, '/root')
    root_node.operations_list = MetaInfo().get_operations()

    # 2) JSON
    check_and_create_if_not_exists(output_dir)
    json_path = os.path.join(output_dir, output_file)
    export_tree(root, json_path, False)

    # 3) pentru afișare
    try:
        node = import_tree(json_path)
        render_tree(node)
    except Exception:
        pass

    # 4) .tree 
    _set_rootdir_from_output_dir(output_dir)
    basename_no_ext = os.path.splitext(output_file)[0]
    simple_render_tree(root_node, basename_no_ext)

    # reconstruire path-ul catre .tree pentru return
    tree_dir = get_abs_file_path(f"boms/{RootDir().get()}")
    tree_path = os.path.join(tree_dir, f"{basename_no_ext}.tree")

    return json_path, tree_path
