import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const expenseApi = {
  // Upload un fichier et créer une dépense
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/expenses/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Lister les dépenses
  list: async (params = {}) => {
    const response = await api.get('/expenses/', { params });
    return response.data;
  },

  // Récupérer une dépense
  get: async (id) => {
    const response = await api.get(`/expenses/${id}`);
    return response.data;
  },

  // Mettre à jour une dépense
  update: async (id, data) => {
    const response = await api.put(`/expenses/${id}`, data);
    return response.data;
  },

  // Supprimer une dépense
  delete: async (id) => {
    const response = await api.delete(`/expenses/${id}`);
    return response.data;
  },

  // Exporter en Excel
  exportExcel: (month, year) => {
    window.open(`/api/expenses/export/excel?month=${month}&year=${year}`, '_blank');
  },

  // Exporter en PDF
  exportPdf: (month, year) => {
    window.open(`/api/expenses/export/pdf?month=${month}&year=${year}`, '_blank');
  },
};

export default api;
