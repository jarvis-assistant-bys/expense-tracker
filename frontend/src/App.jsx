import { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { expenseApi } from './services/api';

const CATEGORIES = [
  { value: 'repas', label: '🍽️ Repas' },
  { value: 'transport', label: '🚗 Transport' },
  { value: 'fournitures', label: '📦 Fournitures' },
  { value: 'logiciel', label: '💻 Logiciel' },
  { value: 'telecommunication', label: '📱 Télécom' },
  { value: 'hebergement', label: '🏨 Hébergement' },
  { value: 'formation', label: '📚 Formation' },
  { value: 'autre', label: '📋 Autre' },
];

function App() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // Charger les dépenses
  const loadExpenses = useCallback(async () => {
    setLoading(true);
    try {
      const data = await expenseApi.list({ month: selectedMonth, year: selectedYear });
      setExpenses(data);
    } catch (error) {
      console.error('Erreur chargement:', error);
    }
    setLoading(false);
  }, [selectedMonth, selectedYear]);

  useEffect(() => {
    loadExpenses();
  }, [loadExpenses]);

  // Upload de fichier
  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    for (const file of acceptedFiles) {
      try {
        await expenseApi.upload(file);
      } catch (error) {
        console.error('Erreur upload:', error);
        alert(`Erreur upload ${file.name}: ${error.response?.data?.detail || error.message}`);
      }
    }
    setUploading(false);
    loadExpenses();
  }, [loadExpenses]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    }
  });

  // Édition
  const startEdit = (expense) => {
    setEditingId(expense.id);
    setEditForm({
      date: expense.date,
      description: expense.description || '',
      amount_ht: expense.amount_ht || '',
      tva: expense.tva || '',
      amount_ttc: expense.amount_ttc || '',
      category: expense.category || 'autre',
      vendor: expense.vendor || '',
    });
  };

  const saveEdit = async () => {
    try {
      await expenseApi.update(editingId, editForm);
      setEditingId(null);
      loadExpenses();
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
      alert('Erreur lors de la sauvegarde');
    }
  };

  const deleteExpense = async (id) => {
    if (!confirm('Supprimer cette dépense ?')) return;
    try {
      await expenseApi.delete(id);
      loadExpenses();
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  // Calcul des totaux
  const totals = expenses.reduce((acc, e) => ({
    ht: acc.ht + (e.amount_ht || 0),
    tva: acc.tva + (e.tva || 0),
    ttc: acc.ttc + (e.amount_ttc || 0),
  }), { ht: 0, tva: 0, ttc: 0 });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">🧾 Expense Tracker</h1>
          <p className="text-gray-600">Gestion des notes de frais</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Zone d'upload */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
          }`}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <div className="text-blue-600">
              <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mb-2"></div>
              <p>Analyse en cours...</p>
            </div>
          ) : (
            <>
              <div className="text-4xl mb-2">📤</div>
              <p className="text-gray-600">
                {isDragActive
                  ? 'Déposez les fichiers ici...'
                  : 'Glissez-déposez vos tickets ou factures (images, PDF)'}
              </p>
              <p className="text-sm text-gray-400 mt-2">ou cliquez pour sélectionner</p>
            </>
          )}
        </div>

        {/* Filtres et exports */}
        <div className="flex flex-wrap items-center gap-4 my-6">
          <div className="flex items-center gap-2">
            <label className="text-gray-600">Période :</label>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
              className="border rounded-lg px-3 py-2"
            >
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  {format(new Date(2024, i), 'MMMM', { locale: fr })}
                </option>
              ))}
            </select>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="border rounded-lg px-3 py-2"
            >
              {[2024, 2025, 2026, 2027].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-2 ml-auto">
            <button
              onClick={() => expenseApi.exportExcel(selectedMonth, selectedYear)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              📊 Excel
            </button>
            <button
              onClick={() => expenseApi.exportPdf(selectedMonth, selectedYear)}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center gap-2"
            >
              📄 PDF
            </button>
          </div>
        </div>

        {/* Liste des dépenses */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
          </div>
        ) : expenses.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-6xl mb-4">📭</div>
            <p>Aucune dépense pour cette période</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Date</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Description</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Catégorie</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">HT</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">TVA</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">TTC</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {expenses.map((expense) => (
                  <tr key={expense.id} className="hover:bg-gray-50">
                    {editingId === expense.id ? (
                      <>
                        <td className="px-4 py-3">
                          <input
                            type="date"
                            value={editForm.date}
                            onChange={(e) => setEditForm({ ...editForm, date: e.target.value })}
                            className="border rounded px-2 py-1 w-full"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="text"
                            value={editForm.description}
                            onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                            className="border rounded px-2 py-1 w-full"
                            placeholder="Description"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <select
                            value={editForm.category}
                            onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                            className="border rounded px-2 py-1 w-full"
                          >
                            {CATEGORIES.map((c) => (
                              <option key={c.value} value={c.value}>{c.label}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            step="0.01"
                            value={editForm.amount_ht}
                            onChange={(e) => setEditForm({ ...editForm, amount_ht: parseFloat(e.target.value) || 0 })}
                            className="border rounded px-2 py-1 w-20 text-right"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            step="0.01"
                            value={editForm.tva}
                            onChange={(e) => setEditForm({ ...editForm, tva: parseFloat(e.target.value) || 0 })}
                            className="border rounded px-2 py-1 w-20 text-right"
                          />
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            step="0.01"
                            value={editForm.amount_ttc}
                            onChange={(e) => setEditForm({ ...editForm, amount_ttc: parseFloat(e.target.value) || 0 })}
                            className="border rounded px-2 py-1 w-20 text-right"
                          />
                        </td>
                        <td className="px-4 py-3 text-center">
                          <button onClick={saveEdit} className="text-green-600 hover:text-green-800 mr-2">✓</button>
                          <button onClick={() => setEditingId(null)} className="text-gray-600 hover:text-gray-800">✕</button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="px-4 py-3 text-sm">
                          {expense.date ? format(new Date(expense.date), 'dd/MM/yyyy') : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm">{expense.description || expense.vendor || '-'}</td>
                        <td className="px-4 py-3 text-sm">
                          {CATEGORIES.find(c => c.value === expense.category)?.label || expense.category}
                        </td>
                        <td className="px-4 py-3 text-sm text-right">{(expense.amount_ht || 0).toFixed(2)} €</td>
                        <td className="px-4 py-3 text-sm text-right">{(expense.tva || 0).toFixed(2)} €</td>
                        <td className="px-4 py-3 text-sm text-right font-medium">{(expense.amount_ttc || 0).toFixed(2)} €</td>
                        <td className="px-4 py-3 text-center">
                          <button onClick={() => startEdit(expense)} className="text-blue-600 hover:text-blue-800 mr-2">✏️</button>
                          <button onClick={() => deleteExpense(expense.id)} className="text-red-600 hover:text-red-800">🗑️</button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50 font-semibold">
                <tr>
                  <td colSpan="3" className="px-4 py-3 text-right">TOTAL</td>
                  <td className="px-4 py-3 text-right">{totals.ht.toFixed(2)} €</td>
                  <td className="px-4 py-3 text-right">{totals.tva.toFixed(2)} €</td>
                  <td className="px-4 py-3 text-right">{totals.ttc.toFixed(2)} €</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
