/**
 * AFAD Yönetim Sistemi - Yardımcı Fonksiyonlar
 */

// Kullanıcı kontrolü
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.pathname.includes('login.html')) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

// Kullanıcı bilgilerini al
function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Çıkış yap
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

// Tarih formatlama
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

// Kısa tarih formatlama
function formatShortDate(dateStr) {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('tr-TR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    }).format(date);
}

// Afet türü çevirisi
const disasterTypeLabels = {
    earthquake: 'Deprem',
    flood: 'Sel',
    fire: 'Yangın',
    landslide: 'Heyelan',
    avalanche: 'Çığ',
    storm: 'Fırtına',
    drought: 'Kuraklık',
    epidemic: 'Salgın',
    other: 'Diğer',
};

function getDisasterTypeLabel(type) {
    return disasterTypeLabels[type] || type;
}

// Şiddet seviyesi çevirisi
const severityLabels = {
    low: 'Düşük',
    medium: 'Orta',
    high: 'Yüksek',
    critical: 'Kritik',
};

function getSeverityLabel(severity) {
    return severityLabels[severity] || severity;
}

// Durum çevirisi
const statusLabels = {
    active: 'Aktif',
    monitoring: 'İzleniyor',
    resolved: 'Çözüldü',
    archived: 'Arşivlendi',
    rescued: 'Kurtarıldı',
    in_shelter: 'Barınakta',
    hospitalized: 'Hastanede',
    missing: 'Kayıp',
    deceased: 'Vefat',
    relocated: 'Yerleştirildi',
    available: 'Mevcut',
    in_use: 'Kullanımda',
    reserved: 'Rezerve',
    depleted: 'Tükendi',
    damaged: 'Hasarlı',
};

function getStatusLabel(status) {
    return statusLabels[status] || status;
}

// Badge class'ı al
function getBadgeClass(type, value) {
    const mapping = {
        severity: {
            low: 'badge-success',
            medium: 'badge-warning',
            high: 'badge-danger',
            critical: 'badge-danger',
        },
        status: {
            active: 'badge-danger',
            monitoring: 'badge-warning',
            resolved: 'badge-success',
            archived: 'badge-info',
        },
        victim_status: {
            rescued: 'badge-success',
            in_shelter: 'badge-info',
            hospitalized: 'badge-warning',
            missing: 'badge-danger',
            deceased: 'badge-dark',
            relocated: 'badge-success',
        },
    };

    return mapping[type]?.[value] || 'badge-info';
}

// Bildirim göster
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 3000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Loading göster/gizle
function showLoading(element) {
    element.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p class="mt-2">Yükleniyor...</p>
        </div>
    `;
}

function hideLoading(element) {
    const loading = element.querySelector('.loading');
    if (loading) {
        loading.remove();
    }
}

// Modal yönetimi
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Form verilerini al
function getFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

// Sayı formatlama
function formatNumber(num) {
    return new Intl.NumberFormat('tr-TR').format(num);
}

// Kategori çevirileri
const categoryLabels = {
    food: 'Gıda',
    water: 'Su',
    medical: 'Tıbbi',
    clothing: 'Giyim',
    shelter: 'Barınma',
    hygiene: 'Hijyen',
    tool: 'Araç-Gereç',
    equipment: 'Ekipman',
    other: 'Diğer',
};

function getCategoryLabel(category) {
    return categoryLabels[category] || category;
}

// Rol çevirileri
const roleLabels = {
    admin: 'Yönetici',
    coordinator: 'Koordinatör',
    field_worker: 'Saha Çalışanı',
    observer: 'Gözlemci',
};

function getRoleLabel(role) {
    return roleLabels[role] || role;
}

// CSS animasyonları
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
