"""
Standard Backend Domain Service Template.
Demonstrates:
- Input validation & custom domain errors
- Separation of concerns (Service -> Repository)
- High testability & clean return types
"""

from dataclasses import dataclass
from typing import Optional


class DomainValidationError(Exception):
    """Raised when a business rule is violated."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ItemDTO:
    id: str
    name: str
    unit_price: float
    quantity: int = 1


class ItemService:
    def __init__(self, repository=None):
        self.repository = repository

    def calculate_subtotal(self, item: ItemDTO) -> float:
        if item.quantity <= 0:
            raise DomainValidationError("Quantity must be greater than zero.", code="INVALID_QUANTITY")
        if item.unit_price < 0:
            raise DomainValidationError("Unit price cannot be negative.", code="INVALID_PRICE")
        
        return round(item.unit_price * item.quantity, 2)
