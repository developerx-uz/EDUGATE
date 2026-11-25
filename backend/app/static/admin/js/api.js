/**
 * EDUGATE API Service Module
 * Handles all backend HTTP calls, JWT tokens, and prefix resolution.
 */
const EdugateAPI = {
    getToken() {
        return localStorage.getItem('edugate_token') || '';
    },

    setToken(token) {
        if (token) {
            localStorage.setItem('edugate_token', token);
        } else {
            localStorage.removeItem('edugate_token');
        }
    },

    getPrefix() {
        if (window.EDUGATE_API_BASE) {
            return window.EDUGATE_API_BASE;
        }
        if (window.location.port === '8000' || window.location.port === '8010') {
            return window.location.pathname.startsWith('/edugate') ? '/edugate' : '';
        }
        if (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '8000' && window.location.port !== '8010')) {
            return 'https://developerx.uz/edugate';
        }
        const path = window.location.pathname;
        if (path.startsWith('/EDUGATE')) return '/EDUGATE';
        if (path.startsWith('/edugate')) return '/edugate';
        return '';
    },

    async request(endpoint, options = {}) {
        let fullUrl = endpoint;
        if (endpoint.startsWith('/api/v1')) {
            fullUrl = this.getPrefix() + endpoint;
        }

        const headers = options.headers ? { ...options.headers } : {};
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        const response = await fetch(fullUrl, {
            ...options,
            headers
        });

        if (response.status === 401) {
            this.setToken('');
            throw new Error('Sessiya muddati tugadi. Iltimos, qayta kiring.');
        }

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Xatolik yuz berdi');
        }

        return data;
    },

    // Auth & Profile
    async login(username, password) {
        const prefix = this.getPrefix();
        const res = await fetch(prefix + '/api/v1/auth/login-json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login yoki parol noto\'g\'ri');
        this.setToken(data.access_token);
        return data;
    },

    async getMe() {
        return await this.request('/api/v1/auth/me');
    },

    async updateProfile(fullName, email) {
        return await this.request('/api/v1/auth/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, email: email })
        });
    },

    async changePassword(currentPassword, newPassword) {
        return await this.request('/api/v1/auth/change-password', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
        });
    },

    // Stats & Real-Time Pulse
    async getPulse() {
        return await this.request('/api/v1/admin/realtime/pulse');
    },

    async getStats() {
        return await this.request('/api/v1/admin/stats');
    },

    async getWeeklyStats() {
        return await this.request('/api/v1/admin/stats/weekly');
    },

    async getReportSummary(period = 'daily') {
        return await this.request('/api/v1/admin/reports/summary?period=' + encodeURIComponent(period));
    },

    async exportReportCsv() {
        const fullUrl = this.getPrefix() + '/api/v1/admin/reports/export-csv';
        const token = this.getToken();
        const res = await fetch(fullUrl, {
            headers: token ? { 'Authorization': 'Bearer ' + token } : {}
        });
        if (res.status === 401) {
            this.setToken('');
            throw new Error('Sessiya muddati tugadi. Iltimos, qayta kiring.');
        }
        if (!res.ok) {
            throw new Error('CSV hisobotni yuklab olishda xatolik');
        }
        return await res.blob();
    },

    // Notifications, Audit, Settings & Leads
    async getNotifications() {
        return await this.request('/api/v1/admin/notifications');
    },

    async getAuditLogs() {
        return await this.request('/api/v1/admin/audit-logs');
    },

    async getSettings() {
        return await this.request('/api/v1/admin/settings');
    },

    async saveSettings(payload) {
        return await this.request('/api/v1/admin/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    },

    async getOrders() {
        return await this.request('/api/v1/orders/');
    },

    async updateOrderStatus(orderId, status) {
        return await this.request('/api/v1/orders/' + orderId, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
    },

    async getAbsenceReasons() {
        return await this.request('/api/v1/attendance/absence-reasons');
    },

    async updateAbsenceStatus(reqId, status) {
        return await this.request('/api/v1/attendance/absence-reasons/' + reqId, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
    },

    // Schools
    async getSchools() {
        return await this.request('/api/v1/admin/schools/detailed');
    },

    async getSchoolClasses(schoolId) {
        return await this.request('/api/v1/admin/schools/' + schoolId + '/classes');
    },

    async createSchool(schoolData) {
        return await this.request('/api/v1/schools/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(schoolData)
        });
    },

    async updateSchool(schoolId, schoolData) {
        return await this.request('/api/v1/admin/schools/' + schoolId, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(schoolData)
        });
    },

    async deleteSchool(schoolId) {
        return await this.request('/api/v1/admin/schools/' + schoolId, {
            method: 'DELETE'
        });
    },

    // 1 Maktab = 1 Login Hisobi
    async getSchoolAccount(schoolId) {
        return await this.request('/api/v1/admin/schools/' + schoolId + '/account');
    },

    async saveSchoolAccount(schoolId, accountData) {
        return await this.request('/api/v1/admin/schools/' + schoolId + '/account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(accountData)
        });
    },

    // Students
    async getStudents(schoolId = '', className = '') {
        let url = '/api/v1/admin/students/all';
        const params = [];
        if (schoolId) params.push('school_id=' + encodeURIComponent(schoolId));
        if (className) params.push('class_name=' + encodeURIComponent(className));
        if (params.length) url += '?' + params.join('&');
        return await this.request(url);
    },

    async createStudent(studentData) {
        return await this.request('/api/v1/students/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });
    },

    async updateStudent(studentId, studentData) {
        return await this.request('/api/v1/admin/students/' + studentId, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });
    },

    async deleteStudent(studentId) {
        return await this.request('/api/v1/admin/students/' + studentId, {
            method: 'DELETE'
        });
    },

    async verifyGovId(docNumber, birthDate) {
        return await this.request('/api/v1/students/verify-gov-id', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_number: docNumber,
                birth_date: birthDate
            })
        });
    },

    // Teachers
    async getTeachers(schoolId = '') {
        let url = '/api/v1/teachers/';
        if (schoolId) url += '?school_id=' + encodeURIComponent(schoolId);
        return await this.request(url);
    },

    async createTeacher(teacherData) {
        return await this.request('/api/v1/teachers/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(teacherData)
        });
    },

    async deleteTeacher(teacherId) {
        return await this.request('/api/v1/teachers/' + teacherId, {
            method: 'DELETE'
        });
    },

    // Devices
    async getDevices() {
        return await this.request('/api/v1/admin/devices/all');
    },

    async createDevice(deviceData) {
        return await this.request('/api/v1/devices/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(deviceData)
        });
    },

    async updateDevice(deviceId, deviceData) {
        return await this.request('/api/v1/devices/' + deviceId, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(deviceData)
        });
    },

    async deleteDevice(deviceId) {
        return await this.request('/api/v1/admin/devices/' + deviceId, {
            method: 'DELETE'
        });
    },

    // Parents
    async getParents() {
        return await this.request('/api/v1/admin/parents');
    },

    async linkParentStudent(payload) {
        return await this.request('/api/v1/parents/link-student', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    },

    // Attendance
    async getTodayLogs(filters = {}) {
        let url = '/api/v1/attendance/today';
        const params = [];
        if (filters.date) params.push('date=' + encodeURIComponent(filters.date));
        if (filters.school_id) params.push('school_id=' + encodeURIComponent(filters.school_id));
        if (filters.class_name) params.push('class_name=' + encodeURIComponent(filters.class_name));
        if (filters.status) params.push('status=' + encodeURIComponent(filters.status));
        if (params.length) url += '?' + params.join('&');
        return await this.request(url);
    }
};

window.EdugateAPI = EdugateAPI;
