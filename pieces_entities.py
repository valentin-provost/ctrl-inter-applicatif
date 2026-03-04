from dataclasses import dataclass, field
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import registry

mapper_registry = registry()

@dataclass
class DataLegoPiece:
    name: str
    color: str
    model_id: int = None
    
    def __post_init__(self):
        self.name = self.name.strip().lower()
        self.color = self.color.strip().lower()

metadata_obj = MetaData()

data_lego_pieces = Table(
    "lego_pieces",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("color", String(50)),
    Column("model_id", Integer, nullable=True)
)

mapper_registry.map_imperatively(DataLegoPiece, data_lego_pieces)