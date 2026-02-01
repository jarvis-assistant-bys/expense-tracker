from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum
from sqlalchemy.sql import func
from datetime import date
import enum
from app.models.database import Base

class ExpenseCategory(str, enum.Enum):
    REPAS = "repas"
    TRANSPORT = "transport"
    FOURNITURES = "fournitures"
    LOGICIEL = "logiciel"
    TELECOMMUNICATION = "telecommunication"
    HEBERGEMENT = "hebergement"
    FORMATION = "formation"
    AUTRE = "autre"

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today)
    description = Column(String(500), nullable=True)
    amount_ht = Column(Float, nullable=True)  # Hors taxes
    tva = Column(Float, nullable=True)  # Montant TVA
    amount_ttc = Column(Float, nullable=False)  # TTC
    tva_rate = Column(Float, nullable=True)  # Taux TVA (20%, 10%, 5.5%)
    category = Column(String(50), default=ExpenseCategory.AUTRE)
    vendor = Column(String(255), nullable=True)  # Fournisseur
    file_path = Column(String(500), nullable=True)  # Chemin du fichier original
    ocr_raw = Column(String(5000), nullable=True)  # Texte brut OCR
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Pour le multi-tenant futur
    user_id = Column(Integer, nullable=True, index=True)
