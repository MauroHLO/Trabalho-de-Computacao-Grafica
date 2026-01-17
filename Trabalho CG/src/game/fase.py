# src/game/fase.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from game.inimigo import Inimigo

Bounds = Tuple[float, float, float, float]  # xmin, xmax, zmin, zmax


@dataclass
class SpawnInfo:
    tipo: str                 # "melee" ou "ranged"
    x: float
    z: float


@dataclass
class Trecho:
    id: int
    nome: str
    bounds: Bounds
    spawns_por_mundo: Dict[int, List[SpawnInfo]]
    chave: bool = False       # conta para liberar o Eco do mundo
    ativo: bool = False
    limpo: bool = False
    inimigos: List[Inimigo] = field(default_factory=list)

    def contem(self, x: float, z: float) -> bool:
        xmin, xmax, zmin, zmax = self.bounds
        return (xmin <= x <= xmax) and (zmin <= z <= zmax)

    def todos_mortos(self) -> bool:
        return all((not e.vivo) for e in self.inimigos)


class Fase:
    """
    Uma fase (mesmo mapa). O que muda por mundo:
      - tint/sky
      - spawns em cada trecho
      - stats/behavior (via cfg_mundo)
    """
    def __init__(self, trechos: List[Trecho], leash_radius: float = 7.0):
        self.trechos = trechos
        self.leash_radius = float(leash_radius)
        self.trecho_atual_id: Optional[int] = None

    def reset_mundo(self):
        for t in self.trechos:
            t.ativo = False
            t.limpo = False
            t.inimigos = []
        self.trecho_atual_id = None

    def get_trecho(self, x: float, z: float) -> Optional[Trecho]:
        for t in self.trechos:
            if t.contem(x, z):
                return t
        return None

    def ativar_trecho(self, t: Trecho, mundo: int, cfg_mundo: dict, cor_inim=(0.55, 0.20, 0.20)):
        if t.ativo:
            return
        t.ativo = True

        inimigos = []
        for sp in t.spawns_por_mundo.get(mundo, []):
            e = Inimigo(sp.x, sp.z, cor_inim, sp.tipo)

            prof = cfg_mundo[sp.tipo]
            # stats por mundo
            e.hp_max = prof.get("hp", getattr(e, "hp_max", 2))
            e.hp = e.hp_max
            e.veloc = prof.get("speed", getattr(e, "veloc", 2.0))
            e.behavior = prof.get("behavior", getattr(e, "behavior", "chase"))

            # ranged extras
            e.cooldown_atk_range = prof.get("fire_cd", getattr(e, "cooldown_atk_range", 2.0))
            e.burst = prof.get("burst", getattr(e, "burst", 1))

            # leash/território
            e.home_x = e.x
            e.home_z = e.z
            e.leash_radius = self.leash_radius
            e.trecho_id = t.id
            e.ativo_no_trecho = False  # acorda quando player entra

            inimigos.append(e)

        t.inimigos = inimigos

    def inimigos_todos(self) -> List[Inimigo]:
        out: List[Inimigo] = []
        for t in self.trechos:
            out.extend(t.inimigos)
        return out

    def update(self, player, mundo: int, cfg_mundo: dict, cor_inim=(0.55, 0.20, 0.20)):
        # detecta trecho atual
        t = self.get_trecho(player.x, player.z)
        novo_id = t.id if t else None
        self.trecho_atual_id = novo_id

        # ativa e acorda inimigos do trecho atual
        if t is not None:
            self.ativar_trecho(t, mundo, cfg_mundo, cor_inim=cor_inim)
            for e in t.inimigos:
                e.ativo_no_trecho = True

        # marca trechos limpos quando todos morrerem
        for trecho in self.trechos:
            if trecho.ativo and (not trecho.limpo) and trecho.todos_mortos():
                trecho.limpo = True

    def mundo_completo(self) -> bool:
        # libera eco quando todos trechos "chave" estiverem limpos
        for t in self.trechos:
            if t.chave and (not t.limpo):
                return False
        return True
