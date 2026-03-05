from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Price:
    amount: float
    currency: str
    formatted: str

@dataclass
class Game:
    id: int
    name: str
    price: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[str] = None
    metacritic_score: Optional[str] = None
    developers: List[str] = field(default_factory=list)
    publishers: List[str] = field(default_factory=list)
    # Nuevos campos
    proton_tier: Optional[str] = None
    hltb_main: Optional[str] = None
    hltb_extra: Optional[str] = None
    hltb_completionist: Optional[str] = None
    pc_requirements_min: Optional[str] = None
    pc_requirements_rec: Optional[str] = None
    # Fase 2: Calidad de Vida
    languages: Optional[str] = None
    controller_support: Optional[str] = None
    multiplayer_modes: List[str] = field(default_factory=list)
    drm_notice: Optional[str] = None

@dataclass
class Deal:
    title: str
    store_name: str
    price: float
    original_price: float
    savings: float
    link: str
    deal_rating: str = "0"
    cheapest_ever_price: Optional[float] = None
    cheapest_ever_date: Optional[int] = None

    @property
    def price_display(self) -> str:
        base = f"{self.price:.2f} USD"
        if self.savings > 0:
            base = f"{self.original_price:.2f} -> {self.price:.2f} USD (-{self.savings:.0f}%)"
        
        if self.cheapest_ever_price is not None and self.price <= self.cheapest_ever_price:
             base += " [¡MÍNIMO HISTÓRICO!]"
        return base

@dataclass
class GameNews:
    title: str
    url: str
    date: int = 0
