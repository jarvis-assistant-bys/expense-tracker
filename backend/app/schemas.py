from pydantic import BaseModel
import datetime
from typing import Optional
from enum import Enum

class ExpenseCategory(str, Enum):
    REPAS = "repas"
    TRANSPORT = "transport"
    FOURNITURES = "fournitures"
    LOGICIEL = "logiciel"
    TELECOMMUNICATION = "telecommunication"
    HEBERGEMENT = "hebergement"
    FORMATION = "formation"
    AUTRE = "autre"

class ExpenseBase(BaseModel):
    date: datetime.date | None = None
    description: str | None = None
    amount_ht: float | None = None
    tva: float | None = None
    amount_ttc: float | None = None
    tva_rate: float | None = None
    category: ExpenseCategory | None = ExpenseCategory.AUTRE
    vendor: str | None = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    file_path: Optional[str] = None
    ocr_raw: Optional[str] = None
    
    class Config:
        from_attributes = True

class OCRResult(BaseModel):
    date: Optional[str] = None
    amount_ttc: Optional[float] = None
    amount_ht: Optional[float] = None
    tva: Optional[float] = None
    tva_rate: Optional[float] = None
    vendor: Optional[str] = None
    raw_text: str

class ExportRequest(BaseModel):
    month: int
    year: int
    format: str = "excel"  # "excel" ou "pdf"
