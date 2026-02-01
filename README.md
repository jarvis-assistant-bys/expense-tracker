# 🧾 Expense Tracker

Application de gestion de notes de frais pour indépendants et entrepreneurs.

## Fonctionnalités

- 📤 Upload de tickets de caisse (images) et factures (PDF)
- 🔍 Extraction automatique via OCR (date, montant HT/TTC, TVA, description)
- 🏷️ Catégorisation des dépenses
- 📊 Export Excel (modifiable)
- 📄 Export PDF (pour comptable)
- 📅 Notes de frais mensuelles

## Stack Technique

### Backend
- Python 3.11+
- FastAPI
- SQLite (dev) / PostgreSQL (prod)
- Tesseract OCR
- openpyxl (Excel)
- weasyprint (PDF)

### Frontend
- React 18
- Vite
- TailwindCSS

## Installation

### Prérequis
- Python 3.11+
- Node.js 18+
- Tesseract OCR (`apt install tesseract-ocr tesseract-ocr-fra`)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Structure

```
expense-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   └── utils/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── README.md
```

## Roadmap

- [x] Structure projet
- [ ] MVP Backend (upload, OCR, CRUD)
- [ ] MVP Frontend (upload, liste, édition)
- [ ] Export Excel
- [ ] Export PDF
- [ ] Authentification
- [ ] Multi-tenant

## License

Propriétaire - Thomas Belardy
