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
        liveTime: '',
        liveDate: '',

        // ===== 3-PORTAL ARCHITECTURE (SUPERADMIN, XALQ TA'LIMI, MAKTABLAR) =====
        portalMode: (() => {
            if (window.EDUGATE_INITIAL_PORTAL) return window.EDUGATE_INITIAL_PORTAL;
            const host = window.location.hostname.toLowerCase();
            if (host.startsWith('journal.') || host.startsWith('school.') || host.startsWith('maktab.')) return 'school';
            if (host.startsWith('edu.') || host.startsWith('monitoring.') || host.startsWith('mmtv.')) return 'monitoring';
            if (host.startsWith('admin.')) return 'admin';

            const path = window.location.pathname.toLowerCase();
            if (path.includes('/journal') || path.includes('/school') || path.includes('/maktab')) return 'school';
            if (path.includes('/edu') || path.includes('/monitoring') || path.includes('/mmtv')) return 'monitoring';
            if (path.includes('/admin')) return 'admin';
            return 'admin';
        })(),

        setPortalMode(mode) {
            this.portalMode = mode;
            this.authError = '';
            if (!this.token) {
                this.loginForm = { username: '', password: '' };
            }
        },

        get isSuperadmin() {
            if (!this.currentUser) return this.portalMode === 'admin';
            const role = (this.currentUser.role || '').toUpperCase();
            return role === 'SUPERADMIN' || this.currentUser.is_superadmin;
        },

        get isMinistryViewer() {
            if (this.currentUser) {
                const role = (this.currentUser.role || '').toUpperCase();
                return role === 'MINISTRY_VIEWER';
            }
            return this.portalMode === 'monitoring';
        },

        get isSchoolAdmin() {
            if (this.currentUser) {
                const role = (this.currentUser.role || '').toUpperCase();
                return role === 'SCHOOL_ADMIN';
            }
            return this.portalMode === 'school';
        },

        get isReadOnly() {
            return this.isMinistryViewer;
        },

        get portalTitle() {
            if (this.isSchoolAdmin) {
                return this.currentUser?.school_name || 'Maktab Kabineti';
            }
            if (this.isMinistryViewer) {
                return "Xalq Ta'limi";
            }
            return 'EDUGATE';
        },

        get portalSubtitle() {
            if (this.isSchoolAdmin) {
                return '1 Maktab = 1 Login';
            }
            if (this.isMinistryViewer) {
                return "Faqat Ko'rish (Read-Only)";
            }
            return 'Server & Tizim Boshqaruvi';
        },

        updateClock() {
            const now = new Date();
            this.liveTime = now.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            this.liveDate = now.toLocaleDateString('uz-UZ', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
        },

        async loginFullscreen() {
            if (!document.fullscreenElement && document.documentElement.requestFullscreen) {
                try {
                    await document.documentElement.requestFullscreen();
                    this.isFullscreen = true;
                } catch (e) {
                    console.warn('Fullscreen request failed:', e);
                }
            }
            await this.login();
        },

        // ===== THEME MANAGEMENT (TO'LIQ OQ & TO'LIQ QORA) =====
        theme: (() => {
            try {
                return localStorage.getItem('edugate_admin_theme') || 'dark';
            } catch (e) {
                return 'dark';
            }
        })(),

        applyTheme(t) {
            this.theme = (t === 'light' || t === 'dark') ? t : 'dark';
            const root = document.documentElement;
            const body = document.body;
            if (this.theme === 'light') {
                root.classList.add('light');
                root.classList.remove('dark');
                if (body) {
                    body.classList.add('theme-light');
                    body.classList.remove('theme-dark');
                }
            } else {
                root.classList.add('dark');
                root.classList.remove('light');
                if (body) {
                    body.classList.add('theme-dark');
                    body.classList.remove('theme-light');
                }
            }
            try {
                localStorage.setItem('edugate_admin_theme', this.theme);
            } catch (e) {}

            try {
                if (window.EdugateCharts && typeof window.EdugateCharts.setTheme === 'function') {
                    window.EdugateCharts.setTheme(this.theme);
                }
            } catch (e) {}
        },

        toggleTheme() {
            const nextTheme = this.theme === 'light' ? 'dark' : 'light';
            this.applyTheme(nextTheme);
        },

        setTheme(t) {
            this.applyTheme(t);
        },

        // ===== NAVIGATION =====
        activeTab: 'dashboard',
        sidebarCollapsed: (() => {
            try {
                const saved = localStorage.getItem('edugate_sidebar_collapsed');
                if (saved !== null) return saved === 'true';
                return false;
            } catch (e) {
                return false;
            }
        })(),
        sidebarOpenMobile: false,
        searchQuery: '',
        showNotifPanel: false,
        showUserMenu: false,
        isFullscreen: false,

        toggleSidebar() {
            if (window.innerWidth < 768) {
                this.sidebarOpenMobile = !this.sidebarOpenMobile;
            } else {
                this.sidebarCollapsed = !this.sidebarCollapsed;
                try {
                    localStorage.setItem('edugate_sidebar_collapsed', this.sidebarCollapsed ? 'true' : 'false');
                } catch (e) {}
                setTimeout(() => {
                    window.dispatchEvent(new Event('resize'));
                }, 310);
            }
        },

        // ===== GLOBAL SEARCH / COMMAND PALETTE =====
        showGlobalSearch: false,
        globalSearchQuery: '',

        openGlobalSearch() {
            this.showGlobalSearch = true;
            this.globalSearchQuery = '';
            if (this.sidebarOpen) this.sidebarOpen = false;
            setTimeout(() => {
                const el = this.$refs.globalSearchInput;
                if (el) el.focus();
            }, 50);
        },

        selectSearchResult(item) {
            this.showGlobalSearch = false;
            if (item.tab) {
                this.activeTab = item.tab;
            }
            if (item.filterKey && item.filterVal) {
                if (item.tab === 'schools') {
                    this.schoolSearchQuery = item.filterVal;
                } else if (item.tab === 'students') {
                    this.studentsFilter.search = item.filterVal;
                }
            }
        },

        get searchFilteredItems() {
            const q = (this.globalSearchQuery || '').trim().toLowerCase();
            const pages = [
                { id: 'p-dash', title: "Dashboard Markazi", subtitle: "Tizim umumiy ko'rsatkichlari va tahlili", tab: 'dashboard', type: "Bo'lim", icon: 'fas fa-chart-pie', bgClass: 'bg-indigo-600/20 text-indigo-400' },
                { id: 'p-sch', title: "Maktablar Boshqaruvi", subtitle: "Barcha ulangan maktablar ro'yxati", tab: 'schools', type: "Bo'lim", icon: 'fas fa-school', bgClass: 'bg-blue-600/20 text-blue-400' },
                { id: 'p-stu', title: "O'quvchilar Kontingenti", subtitle: "Sinflar va o'quvchilar bazasi", tab: 'students', type: "Bo'lim", icon: 'fas fa-user-graduate', bgClass: 'bg-emerald-600/20 text-emerald-400' },
                { id: 'p-tea', title: "O'qituvchilar Tarkibi", subtitle: "Pedagog xodimlar va fanlar", tab: 'teachers', type: "Bo'lim", icon: 'fas fa-chalkboard-user', bgClass: 'bg-purple-600/20 text-purple-400' },
                { id: 'p-att', title: "Davomat Monitoringi", subtitle: "Real-vaqt rejimida jonli davomat", tab: 'attendance', type: "Bo'lim", icon: 'fas fa-clipboard-check', bgClass: 'bg-sky-600/20 text-sky-400' },
                { id: 'p-dev', title: "Kameralar & Turniketlar", subtitle: "Face ID va qurilmalar holati", tab: 'devices', type: "Bo'lim", icon: 'fas fa-video', bgClass: 'bg-amber-600/20 text-amber-400' },
                { id: 'p-par', title: "Ota-onalar Ro'yxati", subtitle: "Telegram botga ulangan profil egalari", tab: 'parents', type: "Bo'lim", icon: 'fas fa-users', bgClass: 'bg-teal-600/20 text-teal-400' },
                { id: 'p-rep', title: "Tahliliy Hisobotlar", subtitle: "Kunlik, oylik hisobotlar va eksport", tab: 'reports', type: "Bo'lim", icon: 'fas fa-chart-bar', bgClass: 'bg-rose-600/20 text-rose-400' },
                { id: 'p-set', title: "Tizim Sozlamalari", subtitle: "Vaqt parametrlari va Telegram sozlamalari", tab: 'settings', type: "Bo'lim", icon: 'fas fa-gear', bgClass: 'bg-slate-700 text-slate-300' }
            ];

            if (!q) return pages;

            const res = [];
            pages.forEach(p => {
                if (p.title.toLowerCase().includes(q) || p.subtitle.toLowerCase().includes(q)) {
                    res.push(p);
                }
            });

            if (Array.isArray(this.schoolsDetailed)) {
                this.schoolsDetailed.forEach(s => {
                    if ((s.name && s.name.toLowerCase().includes(q)) || (s.code && s.code.toLowerCase().includes(q))) {
                        res.push({
                            id: 'sch-' + s.id,
                            title: s.name,
                            subtitle: 'Kodi: ' + s.code + (s.phone ? ' • ' + s.phone : ''),
                            tab: 'schools',
                            filterKey: 'school',
                            filterVal: s.name,
                            type: 'Maktab',
                            icon: 'fas fa-school',
                            bgClass: 'bg-blue-600/20 text-blue-400'
                        });
                    }
                });
            }

            if (Array.isArray(this.students)) {
                this.students.forEach(st => {
                    const fullName = ((st.first_name || '') + ' ' + (st.last_name || '')).toLowerCase();
                    if (fullName.includes(q) || (st.student_code && st.student_code.toLowerCase().includes(q)) || (st.class_name && st.class_name.toLowerCase().includes(q))) {
                        res.push({
                            id: 'stu-' + st.id,
                            title: (st.first_name || '') + ' ' + (st.last_name || ''),
                            subtitle: (st.class_name ? st.class_name + ' sinf • ' : '') + 'Kod: ' + (st.student_code || ''),
                            tab: 'students',
                            filterKey: 'student',
                            filterVal: st.first_name || st.student_code,
                            type: "O'quvchi",
                            icon: 'fas fa-user-graduate',
                            bgClass: 'bg-emerald-600/20 text-emerald-400'
                        });
                    }
                });
            }

            if (Array.isArray(this.devices)) {
                this.devices.forEach(d => {
                    if ((d.name && d.name.toLowerCase().includes(q)) || (d.ip_address && d.ip_address.includes(q))) {
                        res.push({
                            id: 'dev-' + d.id,
                            title: d.name,
                            subtitle: (d.ip_address || '') + (d.device_type ? ' • ' + d.device_type : ''),
                            tab: 'devices',
                            type: 'Qurilma',
                            icon: 'fas fa-video',
                            bgClass: 'bg-amber-600/20 text-amber-400'
                        });
                    }
                });
            }

            return res.slice(0, 15);
        },

        toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().then(() => {
                    this.isFullscreen = true;
                }).catch(err => {
                    console.warn('Fullscreen request failed:', err);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen().then(() => {
                        this.isFullscreen = false;
                    });
                }
            }
        },

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

        // ===== ATTENDANCE MODULE & CCTV HUD =====
        todayLogs: [],
        camViewMode: '2x2',
        liveClock: new Date().toLocaleTimeString('uz-UZ'),
        autoRefresh: true,
        refreshInterval: null,
        attendanceDate: new Date().toISOString().split('T')[0],
        attendanceFilter: { school_id: '', class_name: '', status: '' },

        // ===== REAL-TIME 1-SECOND PULSE ENGINE (PHONE ANTI-FREEZE & SERVER DRIVEN) =====
        isSyncing: false,
        isRefreshing: false,
        realtimeStatus: 'online', // 'online' | 'syncing' | 'offline'
        realtimeTimer: null,
        lastPulseHash: '',
        syncFailures: 0,
        lastSyncTime: '',
        _prevStatsJson: '',
        _visibilityBound: false,

        // ===== PROFILE & SECURITY SETTINGS =====
        currentUser: null,
        profileForm: {
            full_name: '',
            email: ''
        },
        passwordForm: {
            current_password: '',
            new_password: '',
            confirm_password: '',
            show_current: false,
            show_new: false
        },
        isUpdatingProfile: false,
        isUpdatingPassword: false,

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
        showSchoolAccountModal: false,
        showAddStudentModal: false,
        showEditStudentModal: false,
        showAddTeacherModal: false,
        showAddDeviceModal: false,
        showConfirmDialog: false,
        confirmTitle: '',
        confirmMessage: '',
        confirmCallback: null,

        // ===== FORMS =====
        schoolForm: { name: '', code: '', address: '', phone: '', admin_username: '', admin_password: '' },
        editSchoolForm: { id: null },
        schoolAccountForm: { school_id: null, school_name: '', username: '', password: '', full_name: '', has_account: false },
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
            this.applyTheme(this.theme);

            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                    e.preventDefault();
                    if (this.token) {
                        this.openGlobalSearch();
                    }
                }
            });

            document.addEventListener('fullscreenchange', () => {
                this.isFullscreen = !!document.fullscreenElement;
            });

            this.updateClock();
            this.liveClock = new Date().toLocaleTimeString('uz-UZ');
            if (!this._clockInterval) {
                this._clockInterval = setInterval(() => {
                    this.updateClock();
                    this.liveClock = new Date().toLocaleTimeString('uz-UZ');
                }, 1000);
            }

            if (this.token) {
                await this.refreshAllData();
                this.fetchCurrentUser();
                this.startRealtimeEngine();
            } else {
                // Ensure zero autofill on login modal
                this.loginForm = { username: '', password: '' };
                setTimeout(() => {
                    this.loginForm = { username: '', password: '' };
                }, 50);
                setTimeout(() => {
                    this.loginForm = { username: '', password: '' };
                }, 250);
            }
        },

        // ===== REAL-TIME 1-SECOND PULSE ENGINE (PHONE ANTI-FREEZE & SERVER DRIVEN) =====
        startRealtimeEngine() {
            this.stopRealtimeEngine();
            // Boshlanishida birinchi tick
            this.scheduleNextPulse(800);

            // Brauzer yoki telefon ekrani o'chirilganda/yoqilganda avtomatik sezish
            if (!this._visibilityBound) {
                document.addEventListener('visibilitychange', () => {
                    if (!document.hidden && this.token) {
                        this.scheduleNextPulse(100);
                    }
                });
                this._visibilityBound = true;
            }
        },

        stopRealtimeEngine() {
            if (this.realtimeTimer) {
                clearTimeout(this.realtimeTimer);
                this.realtimeTimer = null;
            }
        },

        scheduleNextPulse(delayMs = 1000) {
            if (this.realtimeTimer) {
                clearTimeout(this.realtimeTimer);
            }
            this.realtimeTimer = setTimeout(() => {
                this.performRealtimePulse();
            }, delayMs);
        },

        async performRealtimePulse() {
            // 1. Foydalanuvchi tizimga kirmagan bo'lsa, davom etmaymiz
            if (!this.token) {
                return;
            }

            // 2. QAT'IY BACKPRESSURE: Agar oldingi so'rov hali serverdan javob olmagan bo'lsa ("yetib kelmagan bo'lsa"),
            // yangi so'rov HECH QACHON jo'natilmaydi! Bu telefon qotishlarini va brauzer osilishini 100% oldini oladi.
            if (this.isSyncing) {
                return;
            }

            // 3. Agar foydalanuvchi telefon ekranini qulflagan yoki boshqa ilovaga o'tgan bo'lsa,
            // telefon qizib ketmasligi va batareya tejalishi uchun kechiktiramiz
            if (document.hidden) {
                this.scheduleNextPulse(3000);
                return;
            }

            this.isSyncing = true;
            this.realtimeStatus = 'syncing';

            try {
                // Serverdan yagona tezkor puls so'rovi (faqat va faqat server o'zi beradi)
                const pulse = await EdugateAPI.getPulse();

                // FOYDALANUVCHIGA SERVERDAN JAVOB YETIB KELDI ("OK")
                if (pulse && pulse.status === 'ok') {
                    // Statistika va grafiklar yangilanishi
                    if (pulse.stats) {
                        const sJson = JSON.stringify(pulse.stats);
                        if (this._prevStatsJson !== sJson) {
                            this.stats = pulse.stats;
                            this._prevStatsJson = sJson;
                            if (window.EdugateCharts && typeof window.EdugateCharts.update === 'function') {
                                window.EdugateCharts.update(this.stats, this.weeklyStats);
                            }
                        }
                    }

                    // Jonli davomat loglari (real-time CCTV va jadval)
                    if (Array.isArray(pulse.today_logs)) {
                        this.todayLogs = pulse.today_logs;
                    }

                    // Versiya tekshiruvi: Agar ma'lumotlar bazasida o'zgarish bo'lgan bo'lsa (maktab, o'quvchi va h.k.)
                    if (pulse.version_hash && this.lastPulseHash && pulse.version_hash !== this.lastPulseHash) {
                        if (this.activeTab === 'schools') this.fetchSchoolsDetailed();
                        else if (this.activeTab === 'students') this.fetchAllStudents();
                        else if (this.activeTab === 'teachers') this.fetchAllTeachers();
                        else if (this.activeTab === 'devices') this.fetchDevices();
                        else if (this.activeTab === 'parents') this.fetchParents();
                    }
                    this.lastPulseHash = pulse.version_hash;

                    this.realtimeStatus = 'online';
                    this.syncFailures = 0;
                    this.lastSyncTime = new Date().toLocaleTimeString('uz-UZ');
                } else {
                    this.realtimeStatus = 'offline';
                }
            } catch (err) {
                // Agar server javob bermasa yoki internet uzilsa ("yo'q")
                this.syncFailures++;
                this.realtimeStatus = this.syncFailures > 2 ? 'offline' : 'syncing';
            } finally {
                this.isSyncing = false;
                // SERVERDAN JAVOB OLINGANDAN SO'NG GINA (foydalanuvchi qabul qilib olgach), 
                // AYNAN 1 SEKUND (1000ms) KUTIB KEYINGI TICK YUBORILADI!
                const nextDelay = this.syncFailures > 3 ? 3000 : 1000;
                this.scheduleNextPulse(nextDelay);
            }
        },

        async triggerManualRefresh() {
            if (this.isRefreshing) return;
            this.isRefreshing = true;
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
                this.lastSyncTime = new Date().toLocaleTimeString('uz-UZ');
                this.realtimeStatus = 'online';
                this.showToast("Barcha ma'lumotlar muvaffaqiyatli yangilandi", 'success');
            } catch (e) {
                this.showToast("Yangilashda xatolik: " + (e.message || 'Server xatosi'), 'error');
            } finally {
                this.isRefreshing = false;
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

                // Auto switch portalMode based on returned user role
                const role = (res.role || '').toUpperCase();
                if (role === 'SCHOOL_ADMIN') {
                    this.portalMode = 'school';
                } else if (role === 'MINISTRY_VIEWER') {
                    this.portalMode = 'monitoring';
                } else if (role === 'SUPERADMIN') {
                    if (this.portalMode !== 'school') {
                        this.portalMode = 'admin';
                    }
                }

                this.showToast('Hush kelibsiz! Tizimga muvaffaqiyatli kirdingiz.', 'success');
                await this.initApp();
            } catch (err) {
                this.authError = err.message;
            } finally {
                this.loading = false;
            }
        },

        logout() {
            this.token = '';
            EdugateAPI.setToken('');
            this.loginForm = { username: '', password: '' };
            this.stopRealtimeEngine();
            if (this.refreshInterval) clearInterval(this.refreshInterval);
            this.showToast('Tizimdan chiqildi', 'info');
        },

        // ===== PROFILE & SECURITY SETTINGS METHODS =====
        openProfileSettings() {
            this.activeTab = 'profile';
            this.fetchCurrentUser();
        },

        async fetchCurrentUser() {
            if (!this.token) return;
            try {
                const user = await EdugateAPI.getMe();
                if (user) {
                    this.currentUser = user;
                    this.profileForm.full_name = user.full_name || '';
                    this.profileForm.email = user.email || '';

                    const role = (user.role || '').toUpperCase();
                    if (role === 'SCHOOL_ADMIN') {
                        this.portalMode = 'school';
                        if (user.school_id) {
                            this.studentForm.school_id = user.school_id;
                            this.teacherForm.school_id = user.school_id;
                            this.deviceForm.school_id = user.school_id;
                            this.studentsFilter.school_id = user.school_id;
                            this.teachersFilter.school_id = user.school_id;
                            this.attendanceFilter.school_id = user.school_id;
                        }
                        if (this.activeTab === 'schools' || this.activeTab === 'settings') {
                            this.activeTab = 'dashboard';
                        }
                    } else if (role === 'MINISTRY_VIEWER') {
                        this.portalMode = 'monitoring';
                        if (this.activeTab === 'settings') {
                            this.activeTab = 'dashboard';
                        }
                    }
                }
            } catch (err) {
                console.warn('Foydalanuvchi ma\'lumotlarini yuklashda xatolik:', err);
            }
        },

        // ===== 1 MAKTAB = 1 LOGIN BOSHQARUV USULLARI (SUPERADMIN UCHUN) =====
        onSchoolCodeChange() {
            if (!this.editSchoolForm.id && this.schoolForm.code) {
                const cleanCode = this.schoolForm.code.trim().toLowerCase();
                this.schoolForm.admin_username = 'maktab_' + cleanCode;
                if (!this.schoolForm.admin_password) {
                    this.schoolForm.admin_password = 'Maktab_' + this.schoolForm.code.trim() + '2026!';
                }
            }
        },

        async openSchoolAccountModal(school) {
            this.schoolAccountForm.school_id = school.id;
            this.schoolAccountForm.school_name = school.name;
            this.schoolAccountForm.username = school.admin_username || ('maktab_' + (school.code || '').toLowerCase());
            this.schoolAccountForm.password = '';
            this.schoolAccountForm.full_name = school.admin_full_name || (school.name + " Ma'muri");
            this.schoolAccountForm.has_account = !!school.has_login;
            this.showSchoolAccountModal = true;
            try {
                const acc = await EdugateAPI.getSchoolAccount(school.id);
                if (acc && acc.has_account) {
                    this.schoolAccountForm.username = acc.username;
                    this.schoolAccountForm.full_name = acc.full_name || this.schoolAccountForm.full_name;
                    this.schoolAccountForm.has_account = true;
                }
            } catch (e) {}
        },

        async saveSchoolAccount() {
            if (!this.schoolAccountForm.username) {
                this.showToast('Login nomini kiriting', 'error');
                return;
            }
            if (!this.schoolAccountForm.has_account && (!this.schoolAccountForm.password || this.schoolAccountForm.password.length < 6)) {
                this.showToast('Parol kamida 6 ta belgidan iborat bo\'lishi shart', 'error');
                return;
            }
            try {
                const res = await EdugateAPI.saveSchoolAccount(this.schoolAccountForm.school_id, {
                    username: this.schoolAccountForm.username,
                    password: this.schoolAccountForm.password || undefined,
                    full_name: this.schoolAccountForm.full_name
                });
                this.showToast(res.message || 'Maktab logini saqlandi! (1 maktab = 1 login)', 'success');
                this.showSchoolAccountModal = false;
                this.fetchSchoolsDetailed();
            } catch (e) {
                this.showToast(e.message || 'Xatolik yuz berdi', 'error');
            }
        },

        async saveProfile() {
            this.isUpdatingProfile = true;
            try {
                const updated = await EdugateAPI.updateProfile(this.profileForm.full_name, this.profileForm.email);
                this.currentUser = updated;
                this.showToast('Profil ma\'lumotlari muvaffaqiyatli saqlandi', 'success');
            } catch (err) {
                this.showToast(err.message || 'Profilni saqlashda xatolik', 'error');
            } finally {
                this.isUpdatingProfile = false;
            }
        },

        async savePassword() {
            if (!this.passwordForm.current_password) {
                this.showToast('Hozirgi parolingizni kiriting', 'error');
                return;
            }
            if (!this.passwordForm.new_password || this.passwordForm.new_password.length < 6) {
                this.showToast('Yangi parol kamida 6 ta belgidan iborat bo\'lishi kerak', 'error');
                return;
            }
            if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
                this.showToast('Yangi parollar bir-biriga mos kelmadi', 'error');
                return;
            }

            this.isUpdatingPassword = true;
            try {
                await EdugateAPI.changePassword(this.passwordForm.current_password, this.passwordForm.new_password);
                this.passwordForm.current_password = '';
                this.passwordForm.new_password = '';
                this.passwordForm.confirm_password = '';
                this.showToast('Maxfiy parol muvaffaqiyatli yangilandi!', 'success');
            } catch (err) {
                this.showToast(err.message || 'Parolni yangilashda xatolik', 'error');
            } finally {
                this.isUpdatingPassword = false;
            }
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

