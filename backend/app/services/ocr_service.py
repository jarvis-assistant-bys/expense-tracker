"""
OCR Service pour l'extraction de données des tickets de caisse.
Supporte les tickets multi-TVA (5.5%, 10%, 20%).
"""
import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
from pathlib import Path
import re
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class VATLine:
    """Représente une ligne de TVA extraite d'un ticket."""
    rate: float           # Taux TVA (5.5, 10.0, 20.0)
    amount_ht: float      # Montant HT
    amount_vat: float     # Montant TVA
    
    @property
    def amount_ttc(self) -> float:
        """Calcule le montant TTC."""
        return round(self.amount_ht + self.amount_vat, 2)


@dataclass
class ExtractedData:
    """Données extraites d'un ticket de caisse."""
    date: Optional[datetime] = None
    amount_ttc: Optional[float] = None
    amount_ht: Optional[float] = None
    tva: Optional[float] = None
    tva_rate: Optional[float] = None  # Rétrocompatibilité: taux principal
    description: Optional[str] = None
    vendor: Optional[str] = None
    raw_text: str = ""
    # Nouveau: détail multi-TVA
    vat_lines: List[VATLine] = field(default_factory=list)
    vat_validated: bool = False  # True si les calculs sont cohérents


class OCRService:
    """Service d'extraction OCR pour tickets de caisse."""
    
    # Taux de TVA français valides
    VALID_VAT_RATES = [5.5, 10.0, 20.0]
    
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
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parse un nombre décimal (virgule ou point)."""
        try:
            return float(value.replace(',', '.').replace(' ', ''))
        except (ValueError, AttributeError):
            return None
    
    def parse_amount(self, text: str) -> Optional[float]:
        """Extrait le montant TOTAL TTC d'une chaîne."""
        # Patterns pour les montants totaux français
        patterns = [
            r'TOTAL[:\s]*(\d+[,\.]\d{2})\s*(?:€|EUR)?',
            r'(\d+[,\.]\d{2})\s*€',
            r'€\s*(\d+[,\.]\d{2})',
            r'EUR\s*(\d+[,\.]\d{2})',
            r'(\d+[,\.]\d{2})\s*EUR',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_float(match.group(1))
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
    
    def parse_vat_lines(self, text: str) -> List[VATLine]:
        """
        Extrait TOUTES les lignes TVA d'un ticket.
        
        Patterns supportés:
        - "TVA 10 %    31,82    3,18    35,00"
        - "TVA 20%: HT 11,67 TVA 2,33"
        - "T.V.A. 5,5% : 1,23€"
        
        Returns:
            Liste de VATLine avec rate, amount_ht, amount_vat
        """
        vat_lines = []
        
        # Pattern principal: capture taux + montants sur la même ligne
        # Exemple: "TVA 10 %    31,82    3,18    35,00"
        #          "TVA 20 %    11,67    2,33    14,00"
        main_pattern = r'TVA\s*(\d+[,\.]?\d*)\s*%\s+(\d+[,\.]\d{2})\s+(\d+[,\.]\d{2})'
        
        for match in re.finditer(main_pattern, text, re.IGNORECASE):
            rate = self._parse_float(match.group(1))
            amount_ht = self._parse_float(match.group(2))
            amount_vat = self._parse_float(match.group(3))
            
            if rate and rate in self.VALID_VAT_RATES and amount_ht and amount_vat:
                vat_lines.append(VATLine(
                    rate=rate,
                    amount_ht=amount_ht,
                    amount_vat=amount_vat
                ))
        
        # Si pas de match avec le pattern principal, essayer des patterns alternatifs
        if not vat_lines:
            # Pattern alternatif: "TVA X% : Y,YY€" (montant TVA seul)
            alt_pattern = r'TVA\s*(\d+[,\.]?\d*)\s*%[:\s]*(\d+[,\.]\d{2})'
            
            for match in re.finditer(alt_pattern, text, re.IGNORECASE):
                rate = self._parse_float(match.group(1))
                amount_vat = self._parse_float(match.group(2))
                
                if rate and rate in self.VALID_VAT_RATES and amount_vat:
                    # Calculer HT à partir du taux et de la TVA
                    amount_ht = round(amount_vat / (rate / 100), 2)
                    vat_lines.append(VATLine(
                        rate=rate,
                        amount_ht=amount_ht,
                        amount_vat=amount_vat
                    ))
        
        return vat_lines
    
    def parse_tva(self, text: str) -> tuple[Optional[float], Optional[float]]:
        """
        DEPRECATED: Utiliser parse_vat_lines() pour le multi-TVA.
        Conservé pour rétrocompatibilité.
        
        Retourne le montant TVA total et le taux principal.
        """
        vat_lines = self.parse_vat_lines(text)
        
        if vat_lines:
            total_vat = sum(v.amount_vat for v in vat_lines)
            # Retourner le taux le plus représenté (celui avec le plus gros montant)
            main_rate = max(vat_lines, key=lambda v: v.amount_vat).rate
            return round(total_vat, 2), main_rate
        
        # Fallback: ancien comportement pour les tickets simples
        tva_patterns = [
            r'TVA[:\s]*(\d+[,\.]\d{2})',
            r'T\.V\.A[:\s]*(\d+[,\.]\d{2})',
        ]
        tva_amount = None
        for pattern in tva_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tva_amount = self._parse_float(match.group(1))
                break
        
        # Chercher le taux
        rate_patterns = [
            r'TVA\s*(\d+[,\.]?\d*)\s*%',
            r'(\d+[,\.]?\d*)\s*%',
        ]
        tva_rate = None
        for pattern in rate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rate = self._parse_float(match.group(1))
                if rate and rate in self.VALID_VAT_RATES:
                    tva_rate = rate
                    break
        
        return tva_amount, tva_rate
    
    def extract_data(self, file_path: Path) -> ExtractedData:
        """
        Extrait toutes les données d'un document.
        Supporte les tickets multi-TVA.
        """
        raw_text = self.extract_text(file_path)
        
        # Parse les différents éléments
        date = self.parse_date(raw_text)
        amount_ttc = self.parse_amount(raw_text)
        
        # Nouveau: parsing multi-TVA
        vat_lines = self.parse_vat_lines(raw_text)
        
        # Calculer les totaux depuis les lignes TVA si disponibles
        if vat_lines:
            total_ht = round(sum(v.amount_ht for v in vat_lines), 2)
            total_vat = round(sum(v.amount_vat for v in vat_lines), 2)
            calculated_ttc = round(total_ht + total_vat, 2)
            
            # Validation: vérifier cohérence avec le TTC du ticket
            vat_validated = False
            if amount_ttc:
                # Tolérance de 0.02€ pour les arrondis
                vat_validated = abs(calculated_ttc - amount_ttc) <= 0.02
            
            # Utiliser les totaux calculés
            amount_ht = total_ht
            tva = total_vat
            # Taux principal = celui avec le plus gros montant HT
            tva_rate = max(vat_lines, key=lambda v: v.amount_ht).rate
            
            # Si pas de TTC détecté, utiliser le calculé
            if not amount_ttc:
                amount_ttc = calculated_ttc
        else:
            # Fallback: ancien comportement
            tva, tva_rate = self.parse_tva(raw_text)
            vat_validated = False
            
            # Calculer HT si on a TTC et TVA
            amount_ht = None
            if amount_ttc and tva:
                amount_ht = round(amount_ttc - tva, 2)
            elif amount_ttc and tva_rate:
                amount_ht = round(amount_ttc / (1 + tva_rate / 100), 2)
                tva = round(amount_ttc - amount_ht, 2)
        
        # Première ligne non vide comme vendor potentiel
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        vendor = lines[0] if lines else None
        
        return ExtractedData(
            date=date,
            amount_ttc=amount_ttc,
            amount_ht=amount_ht,
            tva=tva,
            tva_rate=tva_rate,
            vendor=vendor,
            raw_text=raw_text,
            vat_lines=vat_lines,
            vat_validated=vat_validated
        )


# Instance singleton
ocr_service = OCRService()
