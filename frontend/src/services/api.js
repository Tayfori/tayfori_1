/**
 * AFAD Yönetim Sistemi - API Service
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIService {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(),
        };

        try {
            const response = await fetch(url, config);

            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/login.html';
                throw new Error('Oturum süresi doldu');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Bir hata oluştu');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth endpoints
    async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Giriş başarısız');
        }

        this.setToken(data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        return data;
    }

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async getMe() {
        return this.request('/auth/me');
    }

    // Dashboard endpoints
    async getDashboardStats() {
        return this.request('/dashboard/stats');
    }

    async getMapData() {
        return this.request('/dashboard/map-data');
    }

    async getDisasterTypes() {
        return this.request('/dashboard/disaster-types');
    }

    async getNeedsAnalysis(disasterId = null) {
        const query = disasterId ? `?disaster_id=${disasterId}` : '';
        return this.request(`/dashboard/needs-analysis${query}`);
    }

    // Disasters endpoints
    async getDisasters(filters = {}) {
        const query = new URLSearchParams(filters).toString();
        return this.request(`/disasters?${query}`);
    }

    async getDisaster(id) {
        return this.request(`/disasters/${id}`);
    }

    async createDisaster(data) {
        return this.request('/disasters/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateDisaster(id, data) {
        return this.request(`/disasters/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteDisaster(id) {
        return this.request(`/disasters/${id}`, {
            method: 'DELETE',
        });
    }

    // Victims endpoints
    async getVictims(filters = {}) {
        const query = new URLSearchParams(filters).toString();
        return this.request(`/victims?${query}`);
    }

    async getVictim(id) {
        return this.request(`/victims/${id}`);
    }

    async createVictim(data) {
        return this.request('/victims/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateVictim(id, data) {
        return this.request(`/victims/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteVictim(id) {
        return this.request(`/victims/${id}`, {
            method: 'DELETE',
        });
    }

    // Inventory endpoints
    async getInventoryItems(filters = {}) {
        const query = new URLSearchParams(filters).toString();
        return this.request(`/inventory/items?${query}`);
    }

    async getInventoryItem(id) {
        return this.request(`/inventory/items/${id}`);
    }

    async createInventoryItem(data) {
        return this.request('/inventory/items', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateInventoryItem(id, data) {
        return this.request(`/inventory/items/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteInventoryItem(id) {
        return this.request(`/inventory/items/${id}`, {
            method: 'DELETE',
        });
    }

    async createInventoryTransaction(data) {
        return this.request('/inventory/transactions', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getInventorySummary() {
        return this.request('/inventory/summary');
    }

    // Notifications endpoints
    async getNotifications(unreadOnly = false) {
        const query = unreadOnly ? '?unread_only=true' : '';
        return this.request(`/notifications${query}`);
    }

    async markNotificationAsRead(id) {
        return this.request(`/notifications/${id}/read`, {
            method: 'PUT',
        });
    }

    async getUnreadCount() {
        return this.request('/notifications/unread/count');
    }
}

const api = new APIService();
