import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
from pathlib import Path
import re
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class ExtractedData:
    date: Optional[datetime] = None
    amount_ttc: Optional[float] = None
    amount_ht: Optional[float] = None
    tva: Optional[float] = None
    tva_rate: Optional[float] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    raw_text: str = ""

class OCRService:
    def __init__(self, lang: str = "fra+eng"):
        self.lang = lang
    
    def extract_text_from_image(self, image_path: Path) -> str:
        """Extrait le texte d'une image."""
        image = Image.open(image_path)
        # Auto-orientation basée sur les métadonnées EXIF
        image = ImageOps.exif_transpose(image)
        # Convertir en RGB si nécessaire (pour les images RGBA ou P)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        text = pytesseract.image_to_string(image, lang=self.lang)
        return text
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extrait le texte d'un PDF."""
        images = convert_from_path(pdf_path)
        texts = []
        for image in images:
            text = pytesseract.image_to_string(image, lang=self.lang)
            texts.append(text)
        return "\n".join(texts)
    
    def extract_text(self, file_path: Path) -> str:
        """Extrait le texte selon le type de fichier."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self.extract_text_from_pdf(file_path)
        else:
            return self.extract_text_from_image(file_path)
    
    def parse_amount(self, text: str) -> Optional[float]:
        """Extrait un montant d'une chaîne."""
        # Patterns pour les montants français
        patterns = [
            r'(\d+[,\.]\d{2})\s*€',
            r'€\s*(\d+[,\.]\d{2})',
            r'EUR\s*(\d+[,\.]\d{2})',
            r'(\d+[,\.]\d{2})\s*EUR',
            r'TOTAL[:\s]*(\d+[,\.]\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                return float(amount_str)
        return None
    
    def parse_date(self, text: str) -> Optional[datetime]:
        """Extrait une date du texte."""
        # Patterns de dates françaises
        patterns = [
            (r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})', '%d/%m/%Y'),
            (r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{2})', '%d/%m/%y'),
            (r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})', None),
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if fmt:
                        date_str = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                        return datetime.strptime(date_str, fmt.replace('-', '/').replace('.', '/'))
                    else:
                        # Mois en texte
                        months = {
                            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
                            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
                            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
                        }
                        day = int(match.group(1))
                        month = months.get(match.group(2).lower(), 1)
                        year = int(match.group(3))
                        return datetime(year, month, day)
                except ValueError:
                    continue
        return None
    
    def parse_tva(self, text: str) -> tuple[Optional[float], Optional[float]]:
        """Extrait le montant TVA et le taux."""
        # Chercher le montant TVA
        tva_patterns = [
            r'TVA[:\s]*(\d+[,\.]\d{2})',
            r'T\.V\.A[:\s]*(\d+[,\.]\d{2})',
        ]
        tva_amount = None
        for pattern in tva_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tva_amount = float(match.group(1).replace(',', '.'))
                break
        
        # Chercher le taux
        rate_patterns = [
            r'(\d+[,\.]?\d*)\s*%',
            r'TVA\s*(\d+[,\.]?\d*)\s*%',
        ]
        tva_rate = None
        for pattern in rate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rate = float(match.group(1).replace(',', '.'))
                if rate in [5.5, 10, 20]:  # Taux français courants
                    tva_rate = rate
                    break
        
        return tva_amount, tva_rate
    
    def extract_data(self, file_path: Path) -> ExtractedData:
        """Extrait toutes les données d'un document."""
        raw_text = self.extract_text(file_path)
        
        # Parse les différents éléments
        date = self.parse_date(raw_text)
        amount_ttc = self.parse_amount(raw_text)
        tva, tva_rate = self.parse_tva(raw_text)
        
        # Calculer HT si on a TTC et TVA
        amount_ht = None
        if amount_ttc and tva:
            amount_ht = amount_ttc - tva
        elif amount_ttc and tva_rate:
            amount_ht = amount_ttc / (1 + tva_rate / 100)
            tva = amount_ttc - amount_ht
        
        # Première ligne non vide comme vendor potentiel
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        vendor = lines[0] if lines else None
        
        return ExtractedData(
            date=date,
            amount_ttc=amount_ttc,
            amount_ht=round(amount_ht, 2) if amount_ht else None,
            tva=round(tva, 2) if tva else None,
            tva_rate=tva_rate,
            vendor=vendor,
            raw_text=raw_text
        )

ocr_service = OCRService()
