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
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://developerx.uz/edugate';
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

        const headers = options.headers || {};
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

    // Auth
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

    // Stats
    async getStats() {
        return await this.request('/api/v1/admin/stats');
    },

    async getWeeklyStats() {
        return await this.request('/api/v1/admin/stats/weekly');
    },

    getExportUrl() {
        return this.getPrefix() + '/api/v1/admin/reports/export-csv';
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

    // Students
    async getStudents(schoolId = '', className = '') {
        let url = '/api/v1/admin/students/all';
        const params = [];
        if (schoolId) params.push('school_id=' + schoolId);
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
        if (schoolId) url += '?school_id=' + schoolId;
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

    async deleteDevice(deviceId) {
        return await this.request('/api/v1/admin/devices/' + deviceId, {
            method: 'DELETE'
        });
    },

    // Parents
    async getParents() {
        return await this.request('/api/v1/admin/parents');
    },

    // Attendance
    async getTodayLogs() {
        return await this.request('/api/v1/attendance/today');
    }
};

window.EdugateAPI = EdugateAPI;
