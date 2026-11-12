/**
 * EDUGATE Admin Main Application Logic (Alpine.js Controller)
 * Full real-life production logic connecting API, Charts, UI state and Modals.
 */
function adminApp() {
    return {
        // ===== AUTHENTICATION =====
        token: EdugateAPI.getToken(),
        loading: false,
        authError: '',
        loginForm: { username: '', password: '' },
        showPassword: false,

        // ===== NAVIGATION =====
        activeTab: 'dashboard',
        sidebarOpen: false,
        sidebarCollapsed: false,
        searchQuery: '',
        showNotifPanel: false,

        // ===== STATS & DASHBOARD =====
        stats: {
            schools_count: 0,
            students_count: 0,
            teachers_count: 0,
            devices_count: 0,
            parents_count: 0,
            today_entries: 0,
            today_exits: 0,
            today_lates: 0,
            today_ontime: 0
        },
        weeklyStats: [],
        notifications: [],

        // ===== SCHOOLS MODULE =====
        schoolsView: 'schools_list',
        schoolViewMode: 'grid',
        schoolSearchQuery: '',
        schoolsDetailed: [],
        selectedSchool: null,
        schoolClasses: [],
        selectedClass: null,
        classDetailTab: 'students',
        classStudents: [],
        classTeachers: [],

        // ===== STUDENTS MODULE =====
        allStudents: [],
        studentsFilter: { search: '', school_id: '', class_name: '' },
        studentsPage: 1,

        // ===== TEACHERS MODULE =====
        allTeachers: [],
        teachersFilter: { search: '', school_id: '' },

        // ===== ATTENDANCE MODULE =====
        todayLogs: [],
        autoRefresh: true,
        refreshInterval: null,
        attendanceDate: new Date().toISOString().split('T')[0],
        attendanceFilter: { school_id: '', class_name: '', status: '' },

        // ===== DEVICES & PARENTS =====
        devices: [],
        parents: [],

        // ===== REPORTS =====
        reportType: 'daily',

        // ===== SETTINGS =====
        settingsTab: 'general',
        systemSettings: {
            school_start_time: '08:00',
            late_threshold_minutes: 15,
            school_end_time: '14:00',
            language: 'uz',
            telegram_bot_token: '',
            admin_chat_id: '',
            notify_late: true,
            notify_entry: true,
            notify_exit: false
        },

        // ===== MODALS & DIALOGS =====
        showAddSchoolModal: false,
        showAddStudentModal: false,
        showEditStudentModal: false,
        showAddTeacherModal: false,
        showAddDeviceModal: false,
        showConfirmDialog: false,
        confirmTitle: '',
        confirmMessage: '',
        confirmCallback: null,

        // ===== FORMS =====
        schoolForm: { name: '', code: '', address: '', phone: '' },
        editSchoolForm: { id: null },
        studentForm: { school_id: '', first_name: '', last_name: '', class_name: '', student_code: '', rfid_card_id: '', pinfl: '', face_encoding: '', photo_path: '' },
        editStudentForm: { id: null, school_id: '', first_name: '', last_name: '', class_name: '', student_code: '', rfid_card_id: '', pinfl: '' },
        teacherForm: { school_id: '', first_name: '', last_name: '', phone_number: '', subject: '', class_name: '' },
        deviceForm: { school_id: '', name: '', device_type: 'AI_CAMERA', direction: 'IN', ip_address: '', location_description: '' },

        // ===== GOV ID SEARCH & FACE CAPTURE =====
        govDocSearch: '',
        govBirthDateSearch: '',
        searchingGov: false,
        studentPhotoPreview: null,

        // ===== TOASTS =====
        toasts: [],
        toastCount: 0,

        // ===== COMPUTED GETTERS =====
        get filteredSchools() {
            if (!this.schoolSearchQuery) return this.schoolsDetailed;
            const q = this.schoolSearchQuery.toLowerCase();
            return this.schoolsDetailed.filter(s => 
                (s.name || '').toLowerCase().includes(q) || 
                (s.code || '').toLowerCase().includes(q) ||
                (s.address || '').toLowerCase().includes(q)
            );
        },

        get filteredStudents() {
            let list = this.allStudents || [];
            if (this.studentsFilter.search) {
                const q = this.studentsFilter.search.toLowerCase();
                list = list.filter(s => 
                    (s.full_name || (s.first_name + ' ' + s.last_name) || '').toLowerCase().includes(q) || 
                    (s.student_code || '').toLowerCase().includes(q) ||
                    (s.pinfl || '').includes(q) ||
                    (s.rfid_card_id || '').toLowerCase().includes(q)
                );
            }
            if (this.studentsFilter.school_id) {
                list = list.filter(s => s.school_id == this.studentsFilter.school_id);
            }
            if (this.studentsFilter.class_name) {
                list = list.filter(s => (s.class_name || '').toLowerCase().includes(this.studentsFilter.class_name.toLowerCase()));
            }
            return list;
        },

        get paginatedStudents() {
            const start = (this.studentsPage - 1) * 15;
            return this.filteredStudents.slice(start, start + 15);
        },

        get filteredTeachers() {
            let list = this.allTeachers || [];
            if (this.teachersFilter.search) {
                const q = this.teachersFilter.search.toLowerCase();
                list = list.filter(t => 
                    (t.full_name || (t.first_name + ' ' + t.last_name) || '').toLowerCase().includes(q) ||
                    (t.subject || '').toLowerCase().includes(q)
                );
            }
            if (this.teachersFilter.school_id) {
                list = list.filter(t => t.school_id == this.teachersFilter.school_id);
            }
            return list;
        },

        get filteredLogs() {
            let list = this.todayLogs || [];
            if (this.attendanceFilter.school_id) {
                list = list.filter(l => l.school_id == this.attendanceFilter.school_id);
            }
            if (this.attendanceFilter.class_name) {
                list = list.filter(l => (l.class_name || '').toLowerCase().includes(this.attendanceFilter.class_name.toLowerCase()));
            }
            if (this.attendanceFilter.status) {
                list = list.filter(l => l.status === this.attendanceFilter.status);
            }
            return list;
        },

        get onTimeCount() {
            return (this.todayLogs || []).filter(l => l.status === 'ON_TIME').length;
        },
        get lateCount() {
            return (this.todayLogs || []).filter(l => l.status === 'LATE').length;
        },
        get exitCount() {
            return (this.todayLogs || []).filter(l => l.event_type === 'EXIT').length;
        },

        // ===== INITIALIZATION =====
        async initApp() {
            if (this.token) {
                await this.refreshAllData();

                // Periodic real-time background refresh
                if (this.refreshInterval) clearInterval(this.refreshInterval);
                this.refreshInterval = setInterval(() => {
                    if (this.autoRefresh && (this.activeTab === 'dashboard' || this.activeTab === 'attendance')) {
                        this.fetchTodayLogs();
                        this.fetchStats();
                    }
                }, 5000);
            }
        },

        async refreshAllData() {
            try {
                await Promise.all([
                    this.fetchStats(),
                    this.fetchWeeklyStats(),
                    this.fetchSchoolsDetailed(),
                    this.fetchAllStudents(),
                    this.fetchAllTeachers(),
                    this.fetchDevices(),
                    this.fetchParents(),
                    this.fetchTodayLogs()
                ]);

                this.$nextTick(() => {
                    EdugateCharts.init(this.stats, this.weeklyStats);
                });
            } catch (err) {
                console.error("Data refresh error:", err);
            }
        },

        // ===== TOASTS =====
        showToast(message, type = 'success') {
            const id = ++this.toastCount;
            this.toasts.push({ id, message, type });
            setTimeout(() => this.removeToast(id), 4000);
        },

        removeToast(id) {
            this.toasts = this.toasts.filter(t => t.id !== id);
        },

        // ===== CONFIRMATION DIALOG =====
        confirm(title, message, callback) {
            this.confirmTitle = title;
            this.confirmMessage = message;
            this.confirmCallback = callback;
            this.showConfirmDialog = true;
        },

        executeConfirmAction() {
            if (this.confirmCallback) this.confirmCallback();
            this.showConfirmDialog = false;
        },

        // ===== AUTHENTICATION =====
        async login() {
            this.loading = true;
            this.authError = '';
            try {
                const res = await EdugateAPI.login(this.loginForm.username, this.loginForm.password);
                this.token = res.access_token;
                this.showToast('Hush kelibsiz! Tizimga muvaffaqiyatli kirdingiz.', 'success');
                this.initApp();
            } catch (err) {
                this.authError = err.message;
            } finally {
                this.loading = false;
            }
        },

        logout() {
            this.token = '';
            EdugateAPI.setToken('');
            if (this.refreshInterval) clearInterval(this.refreshInterval);
            this.showToast('Tizimdan chiqildi', 'info');
        },

        // ===== DATA FETCH METHODS =====
        async fetchStats() {
            try {
                this.stats = await EdugateAPI.getStats();
                EdugateCharts.update(this.stats, this.weeklyStats);
            } catch (e) {}
        },

        async fetchWeeklyStats() {
            try {
                this.weeklyStats = await EdugateAPI.getWeeklyStats();
                EdugateCharts.update(this.stats, this.weeklyStats);
            } catch (e) {}
        },

        async fetchTodayLogs() {
            try {
                this.todayLogs = await EdugateAPI.getTodayLogs();
            } catch (e) {}
        },

        async fetchSchoolsDetailed() {
            try {
                this.schoolsDetailed = await EdugateAPI.getSchools();
                if (this.schoolsDetailed.length > 0) {
                    if (!this.studentForm.school_id) this.studentForm.school_id = this.schoolsDetailed[0].id;
                    if (!this.teacherForm.school_id) this.teacherForm.school_id = this.schoolsDetailed[0].id;
                    if (!this.deviceForm.school_id) this.deviceForm.school_id = this.schoolsDetailed[0].id;
                }
            } catch (e) {}
        },

        async fetchAllStudents() {
            try {
                this.allStudents = await EdugateAPI.getStudents(
                    this.studentsFilter.school_id,
                    this.studentsFilter.class_name
                );
            } catch (e) {}
        },

        async fetchAllTeachers() {
            try {
                this.allTeachers = await EdugateAPI.getTeachers(this.teachersFilter.school_id);
            } catch (e) {}
        },

        async fetchDevices() {
            try {
                this.devices = await EdugateAPI.getDevices();
            } catch (e) {}
        },

        async fetchParents() {
            try {
                this.parents = await EdugateAPI.getParents();
            } catch (e) {}
        },

        // ===== NAVIGATION HELPERS =====
        selectSchool(school) {
            this.selectedSchool = school;
            this.studentForm.school_id = school.id;
            this.teacherForm.school_id = school.id;
            this.deviceForm.school_id = school.id;
            this.schoolsView = 'school_classes';
            EdugateAPI.getSchoolClasses(school.id)
                .then(res => this.schoolClasses = res)
                .catch(() => {});
        },

        selectClass(cls) {
            this.selectedClass = typeof cls === 'object' ? cls.class_name : cls;
            this.studentForm.class_name = this.selectedClass;
            this.teacherForm.class_name = this.selectedClass;
            this.schoolsView = 'class_detail';
            this.classDetailTab = 'students';
            this.fetchClassStudents();
            this.fetchClassTeachers();
        },

        async fetchClassStudents() {
            if (!this.selectedSchool || !this.selectedClass) return;
            try {
                this.classStudents = await EdugateAPI.getStudents(this.selectedSchool.id, this.selectedClass);
            } catch (e) {}
        },

        async fetchClassTeachers() {
            if (!this.selectedSchool || !this.selectedClass) return;
            try {
                this.classTeachers = await EdugateAPI.getTeachers(this.selectedSchool.id);
                this.classTeachers = this.classTeachers.filter(t => t.class_name === this.selectedClass);
            } catch (e) {}
        },

        // ===== MODAL OPENERS =====
        openSchoolModal() {
            this.editSchoolForm = { id: null };
            this.schoolForm = { name: '', code: '', address: '', phone: '' };
            this.showAddSchoolModal = true;
        },

        openStudentModal() {
            this.studentForm.first_name = '';
            this.studentForm.last_name = '';
            this.studentForm.student_code = '';
            this.studentForm.pinfl = '';
            this.studentForm.rfid_card_id = '';
            this.studentPhotoPreview = null;
            this.showAddStudentModal = true;
        },

        openClassModal() {
            this.studentForm.class_name = '';
            this.showAddStudentModal = true;
        },

        openEditStudentModal(st) {
            this.editStudentForm = {
                id: st.id,
                school_id: st.school_id,
                first_name: st.first_name || (st.full_name ? st.full_name.split(' ')[0] : ''),
                last_name: st.last_name || (st.full_name ? st.full_name.split(' ').slice(1).join(' ') : ''),
                class_name: st.class_name,
                student_code: st.student_code,
                rfid_card_id: st.rfid_card_id || '',
                pinfl: st.pinfl || ''
            };
            this.showEditStudentModal = true;
        },

        // ===== CREATE / UPDATE ACTIONS =====
        async saveSchool() {
            try {
                if (this.editSchoolForm.id) {
                    await EdugateAPI.updateSchool(this.editSchoolForm.id, this.schoolForm);
                    this.showToast('Maktab ma\'lumotlari yangilandi!', 'success');
                } else {
                    await EdugateAPI.createSchool(this.schoolForm);
                    this.showToast('Yangi maktab muvaffaqiyatli saqlandi!', 'success');
                }
                this.showAddSchoolModal = false;
                this.fetchSchoolsDetailed();
                this.fetchStats();
            } catch (e) {
                this.showToast(e.message, 'error');
            }
        },

        async createStudent() {
            try {
                await EdugateAPI.createStudent(this.studentForm);
                this.showToast("O'quvchi muvaffaqiyatli qo'shildi!", 'success');
                this.showAddStudentModal = false;
                this.studentForm.first_name = '';
                this.studentForm.last_name = '';
                this.studentForm.student_code = '';
                this.studentForm.rfid_card_id = '';
                this.studentForm.pinfl = '';
                this.studentPhotoPreview = null;
                this.studentForm.face_encoding = '';

                if (this.schoolsView === 'class_detail') this.fetchClassStudents();
                if (this.selectedSchool) this.selectSchool(this.selectedSchool);
                this.fetchAllStudents();
                this.fetchStats();
            } catch (e) {
                this.showToast(e.message, 'error');
            }
        },

        async updateStudent() {
            try {
                await EdugateAPI.updateStudent(this.editStudentForm.id, this.editStudentForm);
                this.showToast("O'quvchi ma'lumotlari yangilandi!", 'success');
                this.showEditStudentModal = false;
                if (this.schoolsView === 'class_detail') this.fetchClassStudents();
                this.fetchAllStudents();
            } catch (e) {
                this.showToast(e.message, 'error');
            }
        },

        async createTeacher() {
            try {
                await EdugateAPI.createTeacher(this.teacherForm);
                this.showToast("O'qituvchi muvaffaqiyatli qo'shildi!", 'success');
                this.showAddTeacherModal = false;
                this.teacherForm.first_name = '';
                this.teacherForm.last_name = '';
                this.teacherForm.phone_number = '';
                if (this.schoolsView === 'class_detail') this.fetchClassTeachers();
                this.fetchAllTeachers();
                this.fetchStats();
            } catch (e) {
                this.showToast(e.message, 'error');
            }
        },

        async createDevice() {
            try {
                await EdugateAPI.createDevice(this.deviceForm);
                this.showToast('Qurilma / Kamera muvaffaqiyatli ulandi!', 'success');
                this.showAddDeviceModal = false;
                this.deviceForm.name = '';
                this.deviceForm.ip_address = '';
                this.fetchDevices();
                this.fetchStats();
            } catch (e) {
                this.showToast(e.message, 'error');
            }
        },

        // ===== DELETE ACTIONS =====
        deleteStudent(id) {
            this.confirm("O'quvchini o'chirish", "Haqiqatan ham ushbu o'quvchini tizimdan o'chirmoqchimisiz?", async () => {
                try {
                    await EdugateAPI.deleteStudent(id);
                    this.showToast("O'quvchi o'chirildi", 'success');
                    if (this.schoolsView === 'class_detail') this.fetchClassStudents();
                    this.fetchAllStudents();
                    this.fetchStats();
                } catch (e) {
                    this.showToast(e.message, 'error');
                }
            });
        },

        deleteTeacher(id) {
            this.confirm("O'qituvchini o'chirish", "Ushbu o'qituvchini ro'yxatdan o'chirmoqchimisiz?", async () => {
                try {
                    await EdugateAPI.deleteTeacher(id);
                    this.showToast("O'qituvchi o'chirildi", 'success');
                    if (this.schoolsView === 'class_detail') this.fetchClassTeachers();
                    this.fetchAllTeachers();
                    this.fetchStats();
                } catch (e) {
                    this.showToast(e.message, 'error');
                }
            });
        },

        deleteSchool(id) {
            this.confirm("Maktabni o'chirish", "DIQQAT: Maktab va uning barcha sinflari hamda o'quvchilari o'chiriladi!", async () => {
                try {
                    await EdugateAPI.deleteSchool(id);
                    this.showToast("Maktab o'chirildi", 'success');
                    this.schoolsView = 'schools_list';
                    this.fetchSchoolsDetailed();
                    this.fetchStats();
                } catch (e) {
                    this.showToast(e.message, 'error');
                }
            });
        },

        // ===== REAL PHOTO & GOV DATA HANDLING =====
        async searchGovId() {
            if (!this.govDocSearch) {
                this.showToast("Hujjat seriyasi yoki JSHSHIR kiriting", 'warning');
                return;
            }
            this.searchingGov = true;
            try {
                const data = await EdugateAPI.verifyGovId(this.govDocSearch, this.govBirthDateSearch);
                if (data && data.found) {
                    this.studentForm.first_name = data.first_name || '';
                    this.studentForm.last_name = data.last_name || '';
                    this.studentForm.class_name = data.suggested_class || this.studentForm.class_name || '7-A';
                    this.studentForm.pinfl = data.pinfl || '';
                    if (!this.studentForm.student_code) {
                        this.studentForm.student_code = (this.selectedSchool ? this.selectedSchool.code : 'SCH') + '-' + Math.floor(1000 + Math.random()*9000);
                    }
                    this.showToast("Topildi: " + data.first_name + " " + data.last_name, 'success');
                } else {
                    this.showToast("Bazada topilmadi. O'zingiz kiritishingiz mumkin.", 'info');
                }
            } catch (e) {
                this.showToast(e.message, 'error');
            } finally {
                this.searchingGov = false;
            }
        },

        handlePhotoUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                this.studentPhotoPreview = e.target.result;
                // Real base64 payload stored for verification & Face ID recognition
                this.studentForm.face_encoding = e.target.result;
            };
            reader.readAsDataURL(file);
        },

        // ===== EXPORT REAL REPORT (CSV/EXCEL) =====
        exportReport(type) {
            if (type === 'excel' || type === 'csv') {
                const url = EdugateAPI.getExportUrl();
                const a = document.createElement('a');
                a.href = url;
                a.download = `edugate_hisobot_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                this.showToast('Haqiqiy Excel/CSV hisoboti yuklab olinmoqda...', 'success');
            } else if (type === 'pdf') {
                window.print();
            }
        },

        // ===== UTILITY HELPERS =====
        getSchoolName(schoolId) {
            const sc = this.schoolsDetailed.find(s => s.id == schoolId);
            return sc ? sc.name : '';
        },

        formatDate(dateStr) {
            if (!dateStr) return '';
            const d = new Date(dateStr);
            return d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        }
    };
}

window.adminApp = adminApp;

