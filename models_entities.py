from dataclasses import dataclass, field
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import registry

mapper_registry = registry()

@dataclass
class DataLegoModel:
    name: str
    
    def __post_init__(self):
        self.name = self.name.strip().upper()

metadata_obj = MetaData()

data_lego_models = Table(
    "lego_models",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50))
)

mapper_registry.map_imperatively(DataLegoModel, data_lego_models)