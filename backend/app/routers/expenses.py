from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract
from typing import List, Optional
from datetime import date, datetime
from pathlib import Path
import uuid
import shutil

from app.models import get_db, Expense
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse, OCRResult
from app.services import ocr_service, export_service
from app.config import settings

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/upload", response_model=ExpenseResponse)
async def upload_expense(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload un fichier (image ou PDF) et extrait les données via OCR."""
    
    # Vérifier l'extension
    ext = file.filename.split('.')[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Extension non supportée. Autorisées: {settings.ALLOWED_EXTENSIONS}")
    
    # Sauvegarder le fichier
    file_id = str(uuid.uuid4())
    file_path = settings.UPLOAD_DIR / f"{file_id}.{ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extraire les données via OCR
        extracted = ocr_service.extract_data(file_path)
        
        # Créer l'expense
        expense = Expense(
            date=extracted.date.date() if extracted.date else date.today(),
            description=extracted.vendor,  # Utiliser vendor comme description initiale
            amount_ht=extracted.amount_ht,
            tva=extracted.tva,
            amount_ttc=extracted.amount_ttc or 0,
            tva_rate=extracted.tva_rate,
            vendor=extracted.vendor,
            file_path=str(file_path),
            ocr_raw=extracted.raw_text[:5000]  # Limiter la taille
        )
        
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        
        return expense
        
    except Exception as e:
        # Nettoyer le fichier en cas d'erreur
        file_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Erreur lors de l'extraction: {str(e)}")

@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020, le=2100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Liste les dépenses avec filtres optionnels."""
    query = select(Expense)
    
    if month:
        query = query.where(extract('month', Expense.date) == month)
    if year:
        query = query.where(extract('year', Expense.date) == year)
    if category:
        query = query.where(Expense.category == category)
    
    query = query.order_by(Expense.date.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
    """Récupère une dépense par ID."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(404, "Dépense non trouvée")
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Met à jour une dépense."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(404, "Dépense non trouvée")
    
    update_data = expense_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    await db.commit()
    await db.refresh(expense)
    return expense

@router.delete("/{expense_id}")
async def delete_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
    """Supprime une dépense."""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(404, "Dépense non trouvée")
    
    # Supprimer le fichier associé
    if expense.file_path:
        Path(expense.file_path).unlink(missing_ok=True)
    
    await db.delete(expense)
    await db.commit()
    return {"message": "Dépense supprimée"}

@router.get("/export/excel")
async def export_excel(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    db: AsyncSession = Depends(get_db)
):
    """Exporte les dépenses du mois en Excel."""
    query = select(Expense).where(
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).order_by(Expense.date)
    
    result = await db.execute(query)
    expenses = result.scalars().all()
    
    excel_file = export_service.generate_excel(expenses, month, year)
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=note_frais_{month:02d}_{year}.xlsx"}
    )

@router.get("/export/pdf")
async def export_pdf(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    db: AsyncSession = Depends(get_db)
):
    """Exporte les dépenses du mois en PDF."""
    query = select(Expense).where(
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).order_by(Expense.date)
    
    result = await db.execute(query)
    expenses = result.scalars().all()
    
    pdf_file = export_service.generate_pdf(expenses, month, year)
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=note_frais_{month:02d}_{year}.pdf"}
    )
