from __future__ import annotations
import json, os
from typing import Tuple, Optional, Literal
from collections import Counter

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher

from datagen.common.utility import get_abs_file_path

LabelKey = Optional[Literal["productid", "pname"]]  # None => doar structural

def _resolve_path(p: str) -> str:
    """Relativ -> repo via get_abs_file_path; Absolut """
    if os.path.isabs(p):
        return p
    return get_abs_file_path(p)

def _load_bom_as_digraph(path: str, labelkey: LabelKey) -> Tuple[nx.DiGraph, int, Counter]:
    """
    Construieste un DiGraph parinte->copil din JSON si returneaza:
      - graful, id-ul radacinii, si (daca e cazul) multisetul etichetelor
     lab=<label or None>, is_root=<bool>
    """
    with open(_resolve_path(path), "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    next_id = 0

    def add_node(node_obj, is_root=False, parent_id: Optional[int] = None) -> int:
        nonlocal next_id
        this_id = next_id
        next_id += 1

        lab = node_obj.get(labelkey, None) if labelkey else None
        G.add_node(this_id, lab=lab, is_root=is_root)
        if parent_id is not None:
            G.add_edge(parent_id, this_id)

        for child in node_obj.get("children", []):
            add_node(child, False, this_id)

        return this_id

    root_id = add_node(data, is_root=True, parent_id=None)

    labs = Counter(nx.get_node_attributes(G, "lab").values()) if labelkey else Counter()
    return G, root_id, labs

def is_isomorphic_boms(path_a: str, path_b: str, *, labelkey: LabelKey = "productid") -> bool:
    """
    True/False: arborii (BOM-urile) sunt izomorfi *rooted*.
      - labelkey in {"productid","pname"} => izomorfism etichetat pe atributul ales
      - labelkey is None                  => izomorfism strict structural (ignora etichetele)
    """
    G1, r1, labs1 = _load_bom_as_digraph(path_a, labelkey)
    G2, r2, labs2 = _load_bom_as_digraph(path_b, labelkey)

    # Fast-fail
    if G1.number_of_nodes() != G2.number_of_nodes():
        return False

    if labelkey and labs1 != labs2:
        return False

    if labelkey and (G1.nodes[r1].get("lab") != G2.nodes[r2].get("lab")):
        return False

    def node_match(a, b):
        # rooted: root->root obligatoriu
        if a.get("is_root") != b.get("is_root"):
            return False
        # pt etichetat comparam și 'lab', iar pt structural-only ignoram 'lab'
        return True if not labelkey else (a.get("lab") == b.get("lab"))

    GM = DiGraphMatcher(G1, G2, node_match=node_match)
    return GM.is_isomorphic()


def cli_iso(path_a: str, path_b: str, *, labelkey: LabelKey = "productid") -> None:
    res = is_isomorphic_boms(path_a, path_b, labelkey=labelkey)
    label_repr = "none" if labelkey is None else labelkey
    print(f"[ISO] label={label_repr}  {os.path.basename(path_a)}  ~  {os.path.basename(path_b)}  =>  {res}")



