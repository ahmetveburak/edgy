from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Mapped, relationship


class DeclarativeMixin(BaseModel):
    """
    Mixin for declarative base models.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @classmethod
    def declarative(cls) -> Any:
        return cls.generate_model_declarative()

    @classmethod
    def generate_model_declarative(cls) -> Any:
        """
        Transforms a core Saffier table into a Declarative model table.
        """
        Base = cls._meta.registry.declarative_base

        # Build the original table
        fields = {"__table__": cls.table}

        # Generate base
        model_table = type(cls.__name__, (Base,), fields)

        # Make sure if there are foreignkeys, builds the relationships
        for column in cls.table.columns:
            if not column.foreign_keys:
                continue

            # Maps the relationships with the foreign keys and related names
            field = cls.fields.get(column.name)
            mapped_model: Mapped[field.to.__name__] = relationship(field.to.__name__)

            # Adds to the current model
            model_table.__mapper__.add_property(f"{column.name}_relation", mapped_model)

        return model_table
