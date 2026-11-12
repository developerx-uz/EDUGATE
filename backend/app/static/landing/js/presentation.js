/**
 * EDUGATE & e-davomat.net Interactive 9-Slide Presentation Deck
 * Complete standalone presentation engine with autoplay, keyboard shortcuts,
 * fullscreen mode, high-resolution visual previews, and detailed technical specifications.
 * Supports 5 languages: Uzbek (uz), English (en), Russian (ru), Kazakh (kz), Kyrgyz (kg).
 */

const PRESENTATION_SLIDES_I18N = {
    "uz": [
        {
            "id": 1,
            "topic": "01 / TIZIM MAQSADI",
            "title": "e-davomat.net & EDUGATE — Maktablar uchun xavfsizlik va davomat tizimi",
            "overview": "Maktablarda o'quvchilar davomatini qulay yuritish, maktabga begona shaxslar kirishining oldini olish va ota-onalarni real vaqtda xabardor qilish uchun yaratilgan ishonchli apparat-dasturiy majmua.",
            "image": "assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg",
            "imageBadge": "Avtomatlashtirilgan O'tish Mexanizmi",
            "specs": [
                {
                    "label": "Tizim vazifasi",
                    "value": "Davomat va xavfsizlik"
                },
                {
                    "label": "Qamrov",
                    "value": "Umumta'lim maktablari"
                },
                {
                    "label": "Yuzni tanish",
                    "value": "Aqlli kamera tizimi (AI)"
                },
                {
                    "label": "Ma'lumotlar uzatish",
                    "value": "Xavfsiz va ishonchli VPN"
                }
            ],
            "keyPoints": [
                "Qog'oz jurnallar o'rniga to'liq shaffof raqamli ro'yxatga olish",
                "O'quvchi maktab binosiga kirganda va chiqqanda aniq vaqtni sekundigacha qayd qilish",
                "Maktab hududiga begona va ruxsatsiz shaxslarning kirishining 100% oldini olish"
            ]
        },
        {
            "id": 2,
            "topic": "02 / USKUNALAR VA TURNIKETLAR",
            "title": "Maktab kirishidagi qulay va xavfsiz tezkor turniketlar",
            "overview": "Ertalabki gavjum vaqtlarda ham o'quvchilar navbatsiz, tez va erkin kirib-chiqishi uchun maxsus moslashtirilgan mustahkam zanglamaydigan turniketlar. Bolalar xavfsizligi to'liq ta'minlangan.",
            "image": "assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg",
            "imageBadge": "Termiz 11-Maktab Real O'rnatilgan Uskunalar",
            "specs": [
                {
                    "label": "Korpus materiali",
                    "value": "AISI 304 Zanglamas po'lat"
                },
                {
                    "label": "O'tish qulayligi",
                    "value": "Navbatsiz, erkin va tez"
                },
                {
                    "label": "O'tish tezligi",
                    "value": "45-50 kishi / daqiqada"
                },
                {
                    "label": "Bolalar xavfsizligi",
                    "value": "Qisilib qolishdan infraqizil himoya"
                }
            ],
            "keyPoints": [
                "Tirbandlik hosil qilmaydigan tezkor shisha va flap barrier qanotlari",
                "Bolalar qisilib qolishiga qarshi 8 juft infraqizil xavfsizlik datchiklari",
                "Favqulodda holat va yong'in signalizatsiyasida avtomatik ochiq qolish (Anti-panika)"
            ]
        },
        {
            "id": 3,
            "topic": "03 / VILOYAT ANALITIKASI",
            "title": "Surxondaryo viloyati bo'yicha markaziy monitoring xaritasi",
            "overview": "Tuman va shahar xalq ta'limi bo'limlari hamda viloyat hokimligi uchun hududdagi barcha maktablarning davomati va o'quvchilar sonini real vaqt rejimida ko'rsatuvchi interaktiv xarita paneli.",
            "image": "assets/statistika1-DhCv2NLr.png",
            "imageBadge": "Surxondaryo & Respublika Markaziy Monitoring Xaritasi",
            "specs": [
                {
                    "label": "Qamrab olingan maktablar",
                    "value": "948 ta umumta'lim maktabi"
                },
                {
                    "label": "Jami o'quvchilar bazasi",
                    "value": "828,867 nafar o'quvchi"
                },
                {
                    "label": "Faol turniketlar",
                    "value": "2,840 ta xavfsiz o'tish yo'lagi"
                },
                {
                    "label": "Viloyat davomati",
                    "value": "98.4% kunlik ko'rsatkich"
                }
            ],
            "keyPoints": [
                "14 ta tuman va Termiz shahri bo'yicha tezkor statistik tahlil",
                "O'g'il bolalar va qizlar balansi bo'yicha real vaqt grafigi",
                "Hududlar kesimida davomat pasaygan maktablarni oniy aniqlash va tekshirish"
            ]
        },
        {
            "id": 4,
            "topic": "04 / RAQAMLI DAVOMAT",
            "title": "Sinflar kesimida kunlik va oylik elektron hisobotlar",
            "overview": "O'qituvchilar va direktor o'rinbosarlari uchun qog'ozbozlikdan xoli elektron jurnal. Har bir o'quvchining o'quv kunlari, kelgan va dars qoldirgan kunlari sekundigacha aniq hisoblanadi.",
            "image": "assets/edavomat-panel-1-CmvD_PlI.png",
            "imageBadge": "Sinflar & Maktab Boshqaruvi Paneli",
            "specs": [
                {
                    "label": "Hisobot turi",
                    "value": "Avtomatlashtirilgan elektron jurnal"
                },
                {
                    "label": "Aniqlik darajasi",
                    "value": "Sekundigacha kirish-chiqish vaqti"
                },
                {
                    "label": "Eksport formati",
                    "value": "Excel (.xlsx), PDF, API"
                },
                {
                    "label": "Filtrlash imkoni",
                    "value": "Sinf, sana, sababli/sababsiz"
                }
            ],
            "keyPoints": [
                "O'quvchining haqiqiy ishtirok foizi avtomatik hisoblanishi",
                "Vaqtni tejash: o'qituvchi 15 daqiqa davomat olishi shart emas",
                "Soxta belgilashlar va inson omilining to'liq yo'q qilinishi"
            ]
        },
        {
            "id": 5,
            "topic": "05 / YUZNI TANISH (FACE ID)",
            "title": "O'quvchilarni yuzidan bir zumda tanish tizimi",
            "overview": "Har bir o'quvchi maktabga kirishda to'xtab turishi shart emas — aqlli kamera uning yuzini yaqinlashishi bilanoq taniydi va turniketni ochadi.",
            "image": "assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg",
            "imageBadge": "3D WDR Dual-Lens Neyron Biometrik Skaner",
            "specs": [
                {
                    "label": "Tanish usuli",
                    "value": "Aqlli 3D neyron yuzni tanish"
                },
                {
                    "label": "Tanish tezligi",
                    "value": "0.18 soniya (kutishlarsiz)"
                },
                {
                    "label": "Aniqlik darajasi",
                    "value": "99.87% (xatosiz tanish)"
                },
                {
                    "label": "Xotira sig'imi",
                    "value": "50,000+ o'quvchi bazasi"
                }
            ],
            "keyPoints": [
                "O'quvchi ulg'ayganda yoki soch turmagi o'zgarganda ham taniydi",
                "Niqob, ko'zoynak yoki qishki kiyimda ham to'siqsiz tanish",
                "Surat yoki telefon ekranidagi videoni ko'rsatib aldab bo'lmaydi (Anti-Spoofing)"
            ]
        },
        {
            "id": 6,
            "topic": "06 / ELEKTRON JURNAL",
            "title": "Avtomatlashtirilgan elektron jurnal va sinflar davomati",
            "overview": "Turniketlardan o'tgan barcha o'quvchilar ma'lumotlari sinflar kesimida yagona elektron jurnalga to'planadi. O'qituvchilar dars vaqtini davomat olishga sarflamaydi, barchasi soniyalar ichida avtomatik qayd etiladi.",
            "image": "assets/elektron-jadval-BFo-eBY-.png",
            "imageBadge": "Avtomatik e-Maktab & Kundalik Moslashuvi",
            "specs": [
                {
                    "label": "Jurnal formati",
                    "value": "Excel (XLSX), PDF, Onlayn jadval"
                },
                {
                    "label": "Qayd etish aniqligi",
                    "value": "07:58:12 (soniyasigacha aniq vaqt)"
                },
                {
                    "label": "Hisobot turlari",
                    "value": "Sinf, maktab, tuman kesimida"
                },
                {
                    "label": "Integratsiya",
                    "value": "e-maktab (Kundalik) tizimiga to'liq mos"
                }
            ],
            "keyPoints": [
                "Sinf rahbarlari va o'qituvchilarning qog'ozbozlik yukini 100% bartaraf etish",
                "O'quvchilarning darsga kelish va ketish vaqtini shaffof va adolatli qayd etish",
                "Maktab rahbariyati uchun bir zumda umumiy elektron davomat tahlili"
            ]
        },
        {
            "id": 7,
            "topic": "07 / OTA-ONA BILDIRISHNOMASI",
            "title": "Ota-onalarga zumda yetib boruvchi Telegram va SMS xabarlari",
            "overview": "Farzandingiz maktabga kirgan va darsdan so'ng chiqqan zahoti ota-onaning telefoniga aniq vaqt ko'rsatilgan rasmiy xabarnoma keladi.",
            "image": "assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg",
            "imageBadge": "Telegram Bot Orqali Oniy Fotoxabarnoma",
            "specs": [
                {
                    "label": "Xabar yetkazish",
                    "value": "Bir zumda ota-onaga boradi"
                },
                {
                    "label": "Yetkazilish kafolati",
                    "value": "100% har bir ota-onaga"
                },
                {
                    "label": "Xabar turlari",
                    "value": "Oddiy SMS va qulay Telegram bot"
                },
                {
                    "label": "Ota-ona uchun",
                    "value": "Ko'ngil to'liq xotirjam"
                }
            ],
            "keyPoints": [
                "Ota-ona farzandining maktabga yetib borganidan ko'ngli to'liq to'q bo'ladi",
                "Darsdan so'ng maktabdan chiqqan vaqti ham darhol ko'rsatiladi",
                "Ota-ona va maktab ma'muriyati o'rtasida mustahkam ishonch ko'prigi"
            ]
        },
        {
            "id": 8,
            "topic": "08 / MA'LUMOTLAR XAVFSIZLIGI",
            "title": "O'quvchilar ma'lumotlari to'liq va qat'iy himoyalangan",
            "overview": "Maktab va o'quvchilarning ma'lumotlari begona ko'zlardan himoyalangan xavfsiz tizimda saqlanadi. Ma'lumotlarni faqat maktab ma'muriyati ko'ra oladi.",
            "image": "assets/edavomat-panel-4-Cf-FRJvB.png",
            "imageBadge": "Shifrlangan Kriptografik Xavfsizlik Paneli",
            "specs": [
                {
                    "label": "Xavfsizlik darajasi",
                    "value": "100% himoyalangan va maxfiy"
                },
                {
                    "label": "Server joylashuvi",
                    "value": "O'zbekistondagi xavfsiz serverda"
                },
                {
                    "label": "Kirish huquqi",
                    "value": "Faqat maktab rahbariyati uchun"
                },
                {
                    "label": "Ishonchlilik",
                    "value": "Begona shaxslar kira olmaydi"
                }
            ],
            "keyPoints": [
                "Biometrik ma'lumotlar tashqi begona tarmoqqa chiqmaydi",
                "Serverlar O'zbekiston hududida xavfsiz ma'lumotlar markazida joylashgan",
                "Faqat tasdiqlangan maktab direktorlari va inspektorlar kirishi mumkin"
            ]
        },
        {
            "id": 9,
            "topic": "09 / MILLIY GVARDIYA XULOSASI",
            "title": "Tizimning maktablarda tartib-intizomni oshirishdagi amaliy natijasi",
            "overview": "O'zbekiston Respublikasi Milliy Gvardiyasi Surxondaryo viloyati boshqarmasi tomonidan loyihaning ta'lim sifatiga va profilaktikaga ijobiy ta'siri rasman tasdiqlandi.",
            "image": "assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg",
            "imageBadge": "Milliy Gvardiya Xodimlari Bilan Joyidagi Nazorat",
            "specs": [
                {
                    "label": "Mas'ul organ",
                    "value": "O'zbekiston Milliy Gvardiyasi"
                },
                {
                    "label": "Hudud",
                    "value": "Surxondaryo viloyati (Termiz shahri)"
                },
                {
                    "label": "Asosiy natija",
                    "value": "Dars qoldirish 74% ga kamaydi"
                },
                {
                    "label": "Status",
                    "value": "Barcha tumanlarda to'liq tasdiqlangan"
                }
            ],
            "keyPoints": [
                "Maktab hududiga begona shaxslarning kirishi 100% cheklandi",
                "Davomat ko'rsatkichi viloyat bo'yicha 98.4% ga ko'tarildi",
                "Loyiha barcha hududlarda joriy etishga to'liq tavsiya etildi"
            ]
        }
    ],
    "en": [
        {
            "id": 1,
            "topic": "01 / SYSTEM PURPOSE",
            "title": "e-davomat.net & EDUGATE — Integrated School Attendance & Security Suite",
            "overview": "A trusted automated hardware-software ecosystem designed for effortless student attendance tracking, complete prevention of unauthorized visitors, and real-time parent notifications.",
            "image": "assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg",
            "imageBadge": "Automated Access Control Mechanism",
            "specs": [
                {
                    "label": "Core Purpose",
                    "value": "Attendance & Safety"
                },
                {
                    "label": "Target Scope",
                    "value": "Public K-12 Schools"
                },
                {
                    "label": "Biometrics",
                    "value": "AI Facial Recognition"
                },
                {
                    "label": "Data Transport",
                    "value": "Encrypted Secure VPN"
                }
            ],
            "keyPoints": [
                "100% transparent digital logging replacing obsolete paper rosters",
                "Precise logging of entry and exit timestamps down to the exact second",
                "Completely eliminates unauthorized entry into school grounds"
            ]
        },
        {
            "id": 2,
            "topic": "02 / HARDWARE & SPEED GATES",
            "title": "Convenient and Safe High-Speed Turnstiles for School Entrances",
            "overview": "Specially engineered stainless steel turnstiles enabling rapid, queue-free throughput during morning peak hours. Comprehensive physical safety for students is fully guaranteed.",
            "image": "assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg",
            "imageBadge": "Termez School No. 11 Real Deployment",
            "specs": [
                {
                    "label": "Chassis Material",
                    "value": "AISI 304 Stainless Steel"
                },
                {
                    "label": "Throughput Flow",
                    "value": "Queue-free, swift & safe"
                },
                {
                    "label": "Speed Rate",
                    "value": "45-50 students / min"
                },
                {
                    "label": "Child Protection",
                    "value": "Anti-pinch infrared safety array"
                }
            ],
            "keyPoints": [
                "Rapid optical glass and flap wings preventing crowd bottlenecks",
                "8 pairs of dual infrared optical beams preventing accidental pinching",
                "Anti-panic emergency fail-safe with instant automatic opening"
            ]
        },
        {
            "id": 3,
            "topic": "03 / REGIONAL ANALYTICS",
            "title": "Centralized Regional Attendance Monitoring Radar",
            "overview": "An interactive command center panel displaying live school attendance, student counts, and demographic ratios across districts for regional governors and education ministries.",
            "image": "assets/statistika1-DhCv2NLr.png",
            "imageBadge": "Surkhandarya & Regional Control Radar",
            "specs": [
                {
                    "label": "Covered Schools",
                    "value": "948 Public Schools"
                },
                {
                    "label": "Total Student Base",
                    "value": "828,867 Active Students"
                },
                {
                    "label": "Active Gate Lanes",
                    "value": "2,840 Controlled Lanes"
                },
                {
                    "label": "Regional Attendance",
                    "value": "98.4% Daily Average"
                }
            ],
            "keyPoints": [
                "Real-time analytical telemetry across all 14 districts and Termez City",
                "Instant gender balance charts and grade-by-grade distribution",
                "Instant anomaly detection for schools experiencing abnormal absence spikes"
            ]
        },
        {
            "id": 4,
            "topic": "04 / DIGITAL ATTENDANCE",
            "title": "Classroom-by-Classroom Daily and Monthly Digital Reports",
            "overview": "A paperless electronic logbook for educators and school executives. Every student's attendance records, punctual arrivals, and absences are verified down to the exact second.",
            "image": "assets/edavomat-panel-1-CmvD_PlI.png",
            "imageBadge": "School Management & Grade Rosters",
            "specs": [
                {
                    "label": "Report Engine",
                    "value": "Automated Digital Ledger"
                },
                {
                    "label": "Timestamp Precision",
                    "value": "Second-accurate in/out times"
                },
                {
                    "label": "Export Formats",
                    "value": "Excel (.xlsx), PDF, Cloud API"
                },
                {
                    "label": "Filtering Options",
                    "value": "Grade, Date, Excused/Unexcused"
                }
            ],
            "keyPoints": [
                "Automatic real-time calculation of student attendance percentages",
                "Saves 15 minutes per class: teachers focus purely on education",
                "Complete eradication of proxy check-ins and subjective human error"
            ]
        },
        {
            "id": 5,
            "topic": "05 / FACE RECOGNITION (FACE ID)",
            "title": "Instant AI Student Facial Recognition Architecture",
            "overview": "Students don't need to halt at the turnstile — dual-lens AI cameras instantly verify identity on the move and unlock the speed gates seamlessly.",
            "image": "assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg",
            "imageBadge": "3D WDR Dual-Lens Neural Biometric Terminal",
            "specs": [
                {
                    "label": "Recognition Engine",
                    "value": "3D Deep Neural Network"
                },
                {
                    "label": "Verification Latency",
                    "value": "0.18 seconds (zero lag)"
                },
                {
                    "label": "Accuracy Rating",
                    "value": "99.87% precision"
                },
                {
                    "label": "Onboard Capacity",
                    "value": "50,000+ student profiles"
                }
            ],
            "keyPoints": [
                "Adaptive AI adapts seamlessly as children grow or change hairstyles",
                "Works flawlessly with face masks, eyeglasses, and winter hoods",
                "Hardware anti-spoofing rejects printed photos and smartphone videos"
            ]
        },
        {
            "id": 6,
            "topic": "06 / ELECTRONIC LOGBOOK",
            "title": "Automated Digital Attendance Ledger & Grade Synchronization",
            "overview": "Student entry logs from all turnstiles automatically populate unified electronic classroom registers. Teachers eliminate time wasted on manual roll calls.",
            "image": "assets/elektron-jadval-BFo-eBY-.png",
            "imageBadge": "Automated e-Maktab & National SIS Sync",
            "specs": [
                {
                    "label": "Register Format",
                    "value": "Excel (XLSX), PDF, Cloud Tables"
                },
                {
                    "label": "Logging Accuracy",
                    "value": "07:58:12 (second-exact timestamp)"
                },
                {
                    "label": "Report Aggregations",
                    "value": "By Grade, School, District"
                },
                {
                    "label": "Integration",
                    "value": "100% compliant with e-maktab"
                }
            ],
            "keyPoints": [
                "100% elimination of bureaucratic paperwork for homeroom teachers",
                "Transparent and undisputed verification of arrival and departure times",
                "Instant high-level analytics for school directors and ministry inspectors"
            ]
        },
        {
            "id": 7,
            "topic": "07 / PARENT NOTIFICATIONS",
            "title": "Instant Telegram and SMS Alerts Delivered to Parents",
            "overview": "The instant a child steps through the gate upon arrival or departure, an official notification with precise time and photo confirmation lands on parents' smartphones.",
            "image": "assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg",
            "imageBadge": "Instant Photo Alert via Telegram Bot",
            "specs": [
                {
                    "label": "Dispatch Speed",
                    "value": "Instant delivery (<1 sec)"
                },
                {
                    "label": "Delivery Guarantee",
                    "value": "100% verified transmission"
                },
                {
                    "label": "Notification Channels",
                    "value": "Telegram Bot & SMS Gateway"
                },
                {
                    "label": "Parent Value",
                    "value": "Total peace of mind"
                }
            ],
            "keyPoints": [
                "Parents enjoy immediate confidence that their child has safely arrived",
                "Exact dismissal timestamp delivered immediately when leaving school",
                "Establishes a solid foundation of trust between families and school leadership"
            ]
        },
        {
            "id": 8,
            "topic": "08 / DATA SECURITY & PRIVACY",
            "title": "Strictly Enforced Military-Grade Student Data Protection",
            "overview": "School and biometric attendance records are securely stored and encrypted away from public networks. Strictly accessible only by authenticated administrators.",
            "image": "assets/edavomat-panel-4-Cf-FRJvB.png",
            "imageBadge": "Encrypted Cryptographic Security Console",
            "specs": [
                {
                    "label": "Security Level",
                    "value": "100% encrypted & confidential"
                },
                {
                    "label": "Server Hosting",
                    "value": "Secure Datacenter in Uzbekistan"
                },
                {
                    "label": "Access Control",
                    "value": "Role-based administrative rights"
                },
                {
                    "label": "Data Integrity",
                    "value": "Zero third-party exposure"
                }
            ],
            "keyPoints": [
                "Biometric neural templates never leave the private encrypted tunnel",
                "Servers reside domestically in tier-3 certified data centers in Uzbekistan",
                "Granular access restricted strictly to certified principals and inspectors"
            ]
        },
        {
            "id": 9,
            "topic": "09 / NATIONAL GUARD OFFICIAL CONCLUSION",
            "title": "Field-Proven Impact on School Safety & Discipline",
            "overview": "The National Guard Directorate of Surkhandarya Region has officially verified the transformative positive impact of the EDUGATE platform on student discipline and crime prevention.",
            "image": "assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg",
            "imageBadge": "On-Site Joint Inspection with National Guard",
            "specs": [
                {
                    "label": "Endorsing Authority",
                    "value": "National Guard of Uzbekistan"
                },
                {
                    "label": "Region of Pilot",
                    "value": "Surkhandarya (Termez City)"
                },
                {
                    "label": "Core Outcome",
                    "value": "Truancy dropped by 74%"
                },
                {
                    "label": "Validation Status",
                    "value": "Fully certified across all districts"
                }
            ],
            "keyPoints": [
                "100% restriction of unauthorized intruders into school facilities",
                "Regional student attendance raised to an unprecedented 98.4%",
                "Officially recommended for nationwide deployment across all regions"
            ]
        }
    ],
    "ru": [
        {
            "id": 1,
            "topic": "01 / ЦЕЛЬ СИСТЕМЫ",
            "title": "e-davomat.net & EDUGATE — Единый комплекс безопасности и учета посещаемости",
            "overview": "Надежный программно-аппаратный комплекс для удобного учета посещаемости учащихся, предотвращения проникновения посторонних лиц и мгновенного оповещения родителей.",
            "image": "assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg",
            "imageBadge": "Автоматизированный механизм прохода",
            "specs": [
                {
                    "label": "Назначение",
                    "value": "Посещаемость и безопасность"
                },
                {
                    "label": "Охват",
                    "value": "Общеобразовательные школы"
                },
                {
                    "label": "Распознавание",
                    "value": "ИИ камеры (Face ID)"
                },
                {
                    "label": "Передача данных",
                    "value": "Защищенный VPN-канал"
                }
            ],
            "keyPoints": [
                "Полный переход от бумажных журналов к прозрачному цифровому учету",
                "Фиксация времени входа и выхода учащегося с точностью до секунды",
                "100% предотвращение проникновения посторонних лиц на территорию школы"
            ]
        },
        {
            "id": 2,
            "topic": "02 / ОБОРУДОВАНИЕ И ТУРНИКЕТЫ",
            "title": "Удобные и безопасные скоростные турникеты для входа в школу",
            "overview": "Прочные турникеты из нержавеющей стали, адаптированные для быстрого прохода учащихся без очередей в утренние часы пик. Детская безопасность гарантирована.",
            "image": "assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg",
            "imageBadge": "Школа №11 г. Термез — Реальный монтаж",
            "specs": [
                {
                    "label": "Материал корпуса",
                    "value": "Нержавеющая сталь AISI 304"
                },
                {
                    "label": "Комфорт прохода",
                    "value": "Быстро и без очередей"
                },
                {
                    "label": "Пропускная способность",
                    "value": "45-50 чел. / минуту"
                },
                {
                    "label": "Безопасность детей",
                    "value": "ИК-защита от защемления"
                }
            ],
            "keyPoints": [
                "Скоростные стеклянные створки, предотвращающие давку и очереди",
                "8 пар инфракрасных датчиков безопасности против защемления",
                "Режим «Антипаника»: автоматическое открытие при тревоге и пожаре"
            ]
        },
        {
            "id": 3,
            "topic": "03 / РЕГИОНАЛЬНАЯ АНАЛИТИКА",
            "title": "Центральная карта мониторинга посещаемости по регионам",
            "overview": "Интерактивная карта для управлений образования и хокимията, отражающая в реальном времени посещаемость и количество учащихся во всех школах области.",
            "image": "assets/statistika1-DhCv2NLr.png",
            "imageBadge": "Центральная Карта Мониторинга Региона",
            "specs": [
                {
                    "label": "Охвачено школ",
                    "value": "948 общеобразовательных школ"
                },
                {
                    "label": "База учащихся",
                    "value": "828,867 школьников"
                },
                {
                    "label": "Активных турникетов",
                    "value": "2,840 полос прохода"
                },
                {
                    "label": "Посещаемость",
                    "value": "98.4% средний показатель"
                }
            ],
            "keyPoints": [
                "Оперативный анализ по всем районам и городу Термез",
                "График посещаемости в реальном времени с разбивкой по полу и классам",
                "Мгновенное выявление школ со спадом посещаемости для оперативного контроля"
            ]
        },
        {
            "id": 4,
            "topic": "04 / ЦИФРОВОЙ УЧЕТ ПОСЕЩАЕМОСТИ",
            "title": "Ежедневные и ежемесячные электронные отчеты по классам",
            "overview": "Электронный журнал для учителей и директоров, избавляющий от бумажной волокиты. Каждый учебный день и факт посещения фиксируется с точностью до секунды.",
            "image": "assets/edavomat-panel-1-CmvD_PlI.png",
            "imageBadge": "Панель Управления Школой и Классами",
            "specs": [
                {
                    "label": "Тип отчетов",
                    "value": "Автоматизированный электронный журнал"
                },
                {
                    "label": "Точность времени",
                    "value": "Время входа/выхода до секунды"
                },
                {
                    "label": "Формат экспорта",
                    "value": "Excel (.xlsx), PDF, API"
                },
                {
                    "label": "Фильтрация",
                    "value": "Класс, дата, уважительная/без"
                }
            ],
            "keyPoints": [
                "Автоматический расчет реального процента посещаемости каждого ученика",
                "Экономия времени урока: учителю не нужно тратить 15 минут на перекличку",
                "Полное исключение фальсификаций и субъективного человеческого фактора"
            ]
        },
        {
            "id": 5,
            "topic": "05 / РАСПОЗНАВАНИЕ ЛИЦ (FACE ID)",
            "title": "Мгновенное распознавание лиц учащихся на базе ИИ",
            "overview": "Учащимся не нужно останавливаться у турникета — умная двухматричная камера распознает лицо на ходу и мгновенно открывает створки.",
            "image": "assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg",
            "imageBadge": "3D WDR Биометрический Нейро-Терминал",
            "specs": [
                {
                    "label": "Метод распознавания",
                    "value": "Глубокая 3D нейросеть"
                },
                {
                    "label": "Скорость распознавания",
                    "value": "0.18 секунды (мгновенно)"
                },
                {
                    "label": "Точность алгоритма",
                    "value": "99.87% без ошибок"
                },
                {
                    "label": "Объем памяти",
                    "value": "50,000+ шаблонов лиц"
                }
            ],
            "keyPoints": [
                "Адаптивный алгоритм узнает ученика при взрослении и смене прически",
                "Безошибочное срабатывание в масках, очках и зимней одежде",
                "Аппаратный Anti-Spoofing: невозможно обмануть фотографией или видео"
            ]
        },
        {
            "id": 6,
            "topic": "06 / ЭЛЕКТРОННЫЙ ЖУРНАЛ",
            "title": "Автоматизированный электронный журнал и посещаемость классов",
            "overview": "Данные всех прошедших через турникет учащихся собираются в единый журнал по классам. Учителя не тратят время урока на перекличку — всё фиксируется автоматически.",
            "image": "assets/elektron-jadval-BFo-eBY-.png",
            "imageBadge": "Интеграция с e-Maktab и Kundalik",
            "specs": [
                {
                    "label": "Формат журнала",
                    "value": "Excel (XLSX), PDF, Онлайн-таблица"
                },
                {
                    "label": "Точность фиксации",
                    "value": "07:58:12 (время до секунды)"
                },
                {
                    "label": "Виды отчетов",
                    "value": "По классу, школе, району"
                },
                {
                    "label": "Интеграция",
                    "value": "Полная совместимость с e-maktab"
                }
            ],
            "keyPoints": [
                "100% освобождение классных руководителей от бумажной рутины",
                "Прозрачная и объективная фиксация времени прихода и ухода",
                "Мгновенный общий аналитический срез для администрации школы"
            ]
        },
        {
            "id": 7,
            "topic": "07 / УВЕДОМЛЕНИЯ РОДИТЕЛЯМ",
            "title": "Мгновенные Telegram и SMS уведомления для родителей",
            "overview": "В тот же миг, когда ребенок заходит в школу или выходит после занятий, на телефон родителя приходит официальное уведомление с точным временем.",
            "image": "assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg",
            "imageBadge": "Мгновенное фотоуведомление через Telegram",
            "specs": [
                {
                    "label": "Скорость отправки",
                    "value": "Мгновенно родителям"
                },
                {
                    "label": "Гарантия доставки",
                    "value": "100% каждому родителю"
                },
                {
                    "label": "Каналы связи",
                    "value": "Telegram-бот и SMS"
                },
                {
                    "label": "Для родителей",
                    "value": "Полное спокойствие за ребенка"
                }
            ],
            "keyPoints": [
                "Родители всегда уверены, что ребенок вовремя и благополучно дошел до школы",
                "Точное время выхода из школы после уроков фиксируется без задержек",
                "Формирование атмосферы доверия между родителями и администрацией школы"
            ]
        },
        {
            "id": 8,
            "topic": "08 / БЕЗОПАСНОСТЬ ДАННЫХ",
            "title": "Полная и строгая защита персональных данных учащихся",
            "overview": "Данные школы и учащихся защищены от постороннего доступа и хранятся на защищенных серверах. Доступ открыт исключительно руководству учебного заведения.",
            "image": "assets/edavomat-panel-4-Cf-FRJvB.png",
            "imageBadge": "Шифрованная Панель Кибербезопасности",
            "specs": [
                {
                    "label": "Уровень защиты",
                    "value": "100% конфиденциально и надежно"
                },
                {
                    "label": "Локализация данных",
                    "value": "Защищенные дата-центры в Узбекистане"
                },
                {
                    "label": "Права доступа",
                    "value": "Только для руководства школы"
                },
                {
                    "label": "Надежность",
                    "value": "Исключен доступ посторонних лиц"
                }
            ],
            "keyPoints": [
                "Биометрические шаблоны не передаются во внешние публичные сети",
                "Серверы размещены на территории Узбекистана в сертифицированных ЦОД",
                "Авторизованный вход только для верифицированных директоров и инспекторов"
            ]
        },
        {
            "id": 9,
            "topic": "09 / ЗАКЛЮЧЕНИЕ НАЦИОНАЛЬНОЙ ГВАРДИИ",
            "title": "Практический результат внедрения в школах и повышение дисциплины",
            "overview": "Управление Национальной гвардии Республики Узбекистан по Сурхандарьинской области официально подтвердило высокую эффективность проекта в сфере профилактики и безопасности.",
            "image": "assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg",
            "imageBadge": "Контроль на местах с сотрудниками Нацгвардии",
            "specs": [
                {
                    "label": "Ответственный орган",
                    "value": "Национальная гвардия Узбекистана"
                },
                {
                    "label": "Регион",
                    "value": "Сурхандарьинская область (г. Термез)"
                },
                {
                    "label": "Главный результат",
                    "value": "Пропуски уроков снизились на 74%"
                },
                {
                    "label": "Статус",
                    "value": "Официально одобрено во всех районах"
                }
            ],
            "keyPoints": [
                "Проникновение посторонних лиц в школы сократилось на 100%",
                "Показатель посещаемости по области вырос до 98.4%",
                "Проект полностью рекомендован к повсеместному внедрению во всех регионах"
            ]
        }
    ],
    "kz": [
        {
            "id": 1,
            "topic": "01 / ЖҮЙЕ МАҚСАТЫ",
            "title": "e-davomat.net & EDUGATE — Мектептерге арналған қауіпсіздік және қатысу жүйесі",
            "overview": "Оқушылардың қатысуын ыңғайлы жүргізу, мектепке бөгде адамдардың кіруіне жол бермеу және ата-аналарды нақты уақытта хабардар етуге арналған сенімді кешен.",
            "image": "assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg",
            "imageBadge": "Автоматтандырылған Өту Тетігі",
            "specs": [
                {
                    "label": "Жүйе міндеті",
                    "value": "Қатысу және қауіпсіздік"
                },
                {
                    "label": "Қамту аясы",
                    "value": "Жалпы білім беретін мектептер"
                },
                {
                    "label": "Бет-әлпетті тану",
                    "value": "Ақылды ИИ камера жүйесі"
                },
                {
                    "label": "Деректерді жіберу",
                    "value": "Қауіпсіз және сенімді VPN"
                }
            ],
            "keyPoints": [
                "Қағаз журналдардың орнына толықтай ашық цифрлық тіркеу",
                "Оқушының келу және кету уақытын секундқа дейін нақты тіркеу",
                "Мектеп аумағына рұқсатсыз және бөгде адамдардың кіруін 100% болдырмау"
            ]
        },
        {
            "id": 2,
            "topic": "02 / ҚҰРЫЛҒЫЛАР МЕН ТУРНИКЕТТЕР",
            "title": "Мектеп кіреберісіндегі ыңғайлы және қауіпсіз жылдам турникеттер",
            "overview": "Таңғы қарбалас уақытта да оқушылардың кезексіз, жылдам және еркін өтуіне арналған баспайтын болаттан жасалған турникеттер. Балалар қауіпсіздігі толық қамтамасыз етілген.",
            "image": "assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg",
            "imageBadge": "Термез 11-Мектеп Нақты Орнатылған Құрылғылар",
            "specs": [
                {
                    "label": "Корпус материалы",
                    "value": "AISI 304 Тот баспайтын болат"
                },
                {
                    "label": "Өту қолайлылығы",
                    "value": "Кезексіз, еркін және жылдам"
                },
                {
                    "label": "Өту жылдамдығы",
                    "value": "45-50 адам / минутына"
                },
                {
                    "label": "Балалар қауіпсіздігі",
                    "value": "Қысылып қалудан ИҚ қорғаныс"
                }
            ],
            "keyPoints": [
                "Кептеліс тудырмайтын жылдам әйнек және қанатты тосқауылдар",
                "Балалардың қысылып қалуына қарсы 8 жұп инфрақызыл қауіпсіздік датчиктері",
                "Төтенше жағдайлар мен өрт кезінде автоматты ашық қалу (Антипаника)"
            ]
        },
        {
            "id": 3,
            "topic": "03 / АЙМАҚТЫҚ ТАЛДАУ",
            "title": "Сұрхандария облысы бойынша орталық мониторинг картасы",
            "overview": "Аудандық және қалалық білім бөлімдері мен әкімдік үшін барлық мектептердегі оқушылар қатысуын нақты уақыт режимінде көрсететін интерактивті карта панелі.",
            "image": "assets/statistika1-DhCv2NLr.png",
            "imageBadge": "Орталық Аймақтық Мониторинг Картасы",
            "specs": [
                {
                    "label": "Қамтылған мектептер",
                    "value": "948 жалпы білім беру мектебі"
                },
                {
                    "label": "Жалпы оқушылар саны",
                    "value": "828,867 оқушы"
                },
                {
                    "label": "Белсенді турникеттер",
                    "value": "2,840 қауіпсіз өту жолы"
                },
                {
                    "label": "Облыс қатысуы",
                    "value": "98.4% күнделікті көрсеткіш"
                }
            ],
            "keyPoints": [
                "Барлық аудандар мен Термез қаласы бойынша жедел статистика",
                "Ұлдар мен қыздар балансы бойынша нақты уақыт графигі",
                "Қатысуы төмендеген мектептерді бірден анықтау және жедел тексеру"
            ]
        },
        {
            "id": 4,
            "topic": "04 / ЦИФРЛЫҚ ҚАТЫСУ",
            "title": "Сыныптар бойынша күнделікті және айлық электронды есептер",
            "overview": "Мұғалімдер мен директор орынбасарларына арналған қағазсыз электрондық журнал. Әрбір оқушының келуі мен сабақтан қалған күндері секундқа дейін дәл есептеледі.",
            "image": "assets/edavomat-panel-1-CmvD_PlI.png",
            "imageBadge": "Сыныптар мен Мектепті Басқару Панелі",
            "specs": [
                {
                    "label": "Есеп түрі",
                    "value": "Автоматтандырылған электронды журнал"
                },
                {
                    "label": "Дәлдік деңгейі",
                    "value": "Секундқа дейінгі кіру-шығу уақыты"
                },
                {
                    "label": "Экспорт форматы",
                    "value": "Excel (.xlsx), PDF, API"
                },
                {
                    "label": "Сүзу мүмкіндігі",
                    "value": "Сынып, күн, себепті/себепсіз"
                }
            ],
            "keyPoints": [
                "Оқушының нақты қатысу пайызын автоматты түрде есептеу",
                "Уақытты үнемдеу: мұғалім сабақта 15 минут түгендеуге уақыт жұмсамайды",
                "Жалған белгілеулер мен адами факторды толықтай жою"
            ]
        },
        {
            "id": 5,
            "topic": "05 / БЕТ-ӘЛПЕТТІ ТАНУ (FACE ID)",
            "title": "Оқушыларды бет-әлпетінен лезде тану жүйесі",
            "overview": "Оқушының турникет алдында тоқтап тұруы қажет емес — ақылды камера оның жүзін жақындаған сәтте-ақ танып, турникетті ашады.",
            "image": "assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg",
            "imageBadge": "3D WDR Нейрондық Биометриялық Сканер",
            "specs": [
                {
                    "label": "Тану әдісі",
                    "value": "Ақылды 3D нейрондық желі"
                },
                {
                    "label": "Тану жылдамдығы",
                    "value": "0.18 секунд (кідіріссіз)"
                },
                {
                    "label": "Дәлдік деңгейі",
                    "value": "99.87% (қатесіз тану)"
                },
                {
                    "label": "Жад сыйымдылығы",
                    "value": "50,000+ оқушы базасы"
                }
            ],
            "keyPoints": [
                "Оқушы өскенде немесе шаш үлгісі өзгергенде де мінсіз таниды",
                "Маска, көзілдірік немесе қысқы киімде де кедергісіз жұмыс істейді",
                "Суретті немесе телефондағы видеоны көрсетіп алдау мүмкін емес (Anti-Spoofing)"
            ]
        },
        {
            "id": 6,
            "topic": "06 / ЭЛЕКТРОНДЫ ЖУРНАЛ",
            "title": "Автоматтандырылған электрондық журнал және сыныптар қатысуы",
            "overview": "Турникеттерден өткен барлық оқушылардың деректері сыныптар бойынша бірыңғай электронды журналға жиналады. Мұғалімдер сабақ уақытын үнемдейді.",
            "image": "assets/elektron-jadval-BFo-eBY-.png",
            "imageBadge": "Автоматты e-Maktab интеграциясы",
            "specs": [
                {
                    "label": "Журнал форматы",
                    "value": "Excel (XLSX), PDF, Онлайн кесте"
                },
                {
                    "label": "Тіркеу дәлдігі",
                    "value": "07:58:12 (секундқа дейінгі уақыт)"
                },
                {
                    "label": "Есеп түрлері",
                    "value": "Сынып, мектеп, аудан бойынша"
                },
                {
                    "label": "Интеграция",
                    "value": "e-maktab жүйесімен толық үйлесімді"
                }
            ],
            "keyPoints": [
                "Сынып жетекшілерінің қағазбастылық жүктемесін 100% жою",
                "Оқушылардың сабаққа келу және кету уақытын ашық әрі әділ тіркеу",
                "Мектеп басшылығы үшін жалпы электронды қатысуды лезде талдау"
            ]
        },
        {
            "id": 7,
            "topic": "07 / АТА-АНАЛАРҒА ХАБАРЛАМА",
            "title": "Ата-аналарға лезде жететін Telegram және SMS хабарламалары",
            "overview": "Балаңыз мектепке кірген және сабақтан кейін шыққан сәтте ата-ананың телефонына нақты уақыты көрсетілген ресми хабарлама келеді.",
            "image": "assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg",
            "imageBadge": "Telegram Бот Арқылы Лезде Фотохабарлама",
            "specs": [
                {
                    "label": "Хабар жеткізу",
                    "value": "Бір сәтте ата-анаға жетеді"
                },
                {
                    "label": "Жеткізу кепілдігі",
                    "value": "100% әрбір ата-анаға"
                },
                {
                    "label": "Хабарлама түрлері",
                    "value": "Қарапайым SMS және Telegram бот"
                },
                {
                    "label": "Ата-аналар үшін",
                    "value": "Көңіл толық тыныш"
                }
            ],
            "keyPoints": [
                "Ата-ана баласының мектепке аман-есен жеткеніне толықтай сенімді болады",
                "Сабақтан кейін мектептен шыққан уақыты да дереу көрсетіледі",
                "Ата-ана мен мектеп әкімшілігі арасындағы берік сенім көпірі"
            ]
        },
        {
            "id": 8,
            "topic": "08 / ДЕРЕКТЕР ҚАУІПСІЗДІГІ",
            "title": "Оқушылардың деректері толық және қатаң қорғалған",
            "overview": "Мектеп пен оқушылардың мәліметтері бөгде көздерден қорғалған қауіпсіз жүйеде сақталады. Ақпаратты тек мектеп басшылығы көре алады.",
            "image": "assets/edavomat-panel-4-Cf-FRJvB.png",
            "imageBadge": "Шифрланған Криптографиялық Қауіпсіздік Панелі",
            "specs": [
                {
                    "label": "Қауіпсіздік деңгейі",
                    "value": "100% қорғалған және құпия"
                },
                {
                    "label": "Сервер орналасуы",
                    "value": "Өзбекстандағы қауіпсіз серверде"
                },
                {
                    "label": "Кіру құқығы",
                    "value": "Тек мектеп басшылығы үшін"
                },
                {
                    "label": "Сенімділік",
                    "value": "Бөгде адамдар кіре алмайды"
                }
            ],
            "keyPoints": [
                "Биометриялық деректер сыртқы бөгде желілерге шықпайды",
                "Серверлер Өзбекстан аумағындағы қауіпсіз деректер орталығында орналасқан",
                "Тек расталған мектеп директорлары мен инспекторлар ғана кіре алады"
            ]
        },
        {
            "id": 9,
            "topic": "09 / ҰЛТТЫҚ ҰЛАН ҚОРЫТЫНДЫСЫ",
            "title": "Жүйенің мектептерде тәртіпті арттырудағы практикалық нәтижесі",
            "overview": "Өзбекстан Республикасы Ұлттық ұланы Сұрхандария облыстық басқармасы жобаның оқу сапасы мен құқық бұзушылықтың алдын алуға оң әсерін ресми түрде растады.",
            "image": "assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg",
            "imageBadge": "Ұлттық Ұлан Қызметкерлерімен Орында Бақылау",
            "specs": [
                {
                    "label": "Жауапты орган",
                    "value": "Өзбекстан Ұлттық ұланы"
                },
                {
                    "label": "Аймақ",
                    "value": "Сұрхандария облысы (Термез қаласы)"
                },
                {
                    "label": "Негізгі нәтиже",
                    "value": "Сабақтан қалу 74%-ға азайды"
                },
                {
                    "label": "Мәртебесі",
                    "value": "Барлық аудандарда толық мақұлданған"
                }
            ],
            "keyPoints": [
                "Мектеп аумағына бөгде адамдардың кіруіне 100% шектеу қойылды",
                "Облыс бойынша қатысу көрсеткіші 98.4%-ға дейін артты",
                "Жоба барлық аймақтарда енгізуге толығымен ұсынылды"
            ]
        }
    ],
    "kg": [
        {
            "id": 1,
            "topic": "01 / СИСТЕМА МАКСАТЫ",
            "title": "e-davomat.net & EDUGATE — Мектептер үчүн коопсуздук жана катышуу системасы",
            "overview": "Окуучулардын катышуусун ыңгайлуу жүргүзүү, мектепке бөтөн адамдардын киришине жол бербөө жана ата-энелерге реалдуу убакытта кабар берүүчү ишенимдүү комплекс.",
            "image": "assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg",
            "imageBadge": "Автоматташтырылган Өтүү Механизми",
            "specs": [
                {
                    "label": "Система милдети",
                    "value": "Катышуу жана коопсуздук"
                },
                {
                    "label": "Камтуу",
                    "value": "Жалпы билим берүүчү мектептер"
                },
                {
                    "label": "Жүздү таануу",
                    "value": "Акылдуу ИИ камера системасы"
                },
                {
                    "label": "Маалымат берүү",
                    "value": "Коопсуз жана ишенимдүү VPN"
                }
            ],
            "keyPoints": [
                "Кагаз журналдардын ордуна толук ачык санариптик эсепке алуу",
                "Окуучунун келүү жана кетүү убактысын секундасына чейин так каттоо",
                "Мектеп аймагына бөтөн адамдардын киришинин 100% алдын алуу"
            ]
        },
        {
            "id": 2,
            "topic": "02 / ЖАБДУУЛАР ЖАНА ТУРНИКЕТТЕР",
            "title": "Мектеп кире беришиндеги ыңгайлуу жана коопсуз ылдам турникеттер",
            "overview": "Эртең мененки убакта окуучулардын кезексиз, тез жана эркин өтүшү үчүн атайын ылайыкташтырылган дат баспаган болот турникеттер. Балдардын коопсуздугу толук камсыздалган.",
            "image": "assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg",
            "imageBadge": "Термез 11-Мектеп Чыныгы Орнотулган Жабдуулар",
            "specs": [
                {
                    "label": "Корпус материалы",
                    "value": "AISI 304 Дат баспаган болот"
                },
                {
                    "label": "Өтүү ыңгайлуулугу",
                    "value": "Кезексиз, эркин жана тез"
                },
                {
                    "label": "Өтүү ылдамдыгы",
                    "value": "45-50 адам / мүнөтүнө"
                },
                {
                    "label": "Балдар коопсуздугу",
                    "value": "Кысылып калуудан ИК коргоо"
                }
            ],
            "keyPoints": [
                "Тыгын жаратпаган ылдам айнек жана канаттуу тосмолор",
                "Балдар кысылып калуусуна каршы 8 жуп инфракызыл сенсорлор",
                "Өзгөчө кырдаалда автоматтык түрдө ачык калуу (Антипаника)"
            ]
        },
        {
            "id": 3,
            "topic": "03 / АЙМАКТЫК ТАЛДОО",
            "title": "Сурхандарыя облусу боюнча борбордук мониторинг картасы",
            "overview": "Райондук жана шаардык билим берүү бөлүмдөрү үчүн бардык мектептердин катышуу көрсөткүчүн реалдуу убакыт режиминде көрсөтүүчү интерактивдүү карта панели.",
            "image": "assets/statistika1-DhCv2NLr.png",
            "imageBadge": "Борбордук Аймактык Мониторинг Картасы",
            "specs": [
                {
                    "label": "Камтылган мектептер",
                    "value": "948 жалпы билим берүүчү мектеп"
                },
                {
                    "label": "Жалпы окуучулар базасы",
                    "value": "828,867 окуучу"
                },
                {
                    "label": "Активдүү турникеттер",
                    "value": "2,840 өтүү тилкеси"
                },
                {
                    "label": "Облус катышуусу",
                    "value": "98.4% күнүмдүк көрсөткүч"
                }
            ],
            "keyPoints": [
                "Бардык райондор жана Термез шаары боюнча ыкчам статистика",
                "Уулдар жана кыздар балансы боюнча реалдуу убакыт графиги",
                "Катышуусу төмөндөгөн мектептерди заматта аныктоо жана текшерүү"
            ]
        },
        {
            "id": 4,
            "topic": "04 / САНАРИПТИК КАТЫШУУ",
            "title": "Класстар боюнча күнүмдүк жана айлык электрондук отчеттор",
            "overview": "Мугалимдер жана директордун орун басарлары үчүн кагазсыз электрондук журнал. Ар бир окуучунун окуу күндөрү, келген жана калтырган күндөрү так эсептелет.",
            "image": "assets/edavomat-panel-1-CmvD_PlI.png",
            "imageBadge": "Класстар жана Мектепти Башкаруу Панели",
            "specs": [
                {
                    "label": "Отчет түрү",
                    "value": "Автоматташтырылган электрондук журнал"
                },
                {
                    "label": "Тактык деңгээли",
                    "value": "Секундасына чейин кирүү-чыгуу убактысы"
                },
                {
                    "label": "Экспорт форматы",
                    "value": "Excel (.xlsx), PDF, API"
                },
                {
                    "label": "Фильтрлөө",
                    "value": "Класс, күн, себептүү/себепсиз"
                }
            ],
            "keyPoints": [
                "Окуучунун реалдуу катышуу пайызын автоматтык эсептөө",
                "Убакытты үнөмдөө: мугалим 15 мүнөт тизме алууга коротпойт",
                "Жалган белгилөөлөрдү жана адам факторун толук жок кылуу"
            ]
        },
        {
            "id": 5,
            "topic": "05 / ЖҮЗДҮ ТААНУУ (FACE ID)",
            "title": "Окуучуларды жүзүнөн заматта таануу системасы",
            "overview": "Ар бир окуучу турникет алдында токтоп калуусу талап кылынбайт — акылдуу камера жүзүн жакындаганда эле таанып, турникетти ачат.",
            "image": "assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg",
            "imageBadge": "3D WDR Нейрондук Биометрикалык Сканер",
            "specs": [
                {
                    "label": "Таануу ыкмасы",
                    "value": "Акылдуу 3D нейрон тармагы"
                },
                {
                    "label": "Таануу ылдамдыгы",
                    "value": "0.18 секунд (күтүүсүз)"
                },
                {
                    "label": "Тактык деңгээли",
                    "value": "99.87% (катасыз таануу)"
                },
                {
                    "label": "Эс тутум көлөмү",
                    "value": "50,000+ окуучу базасы"
                }
            ],
            "keyPoints": [
                "Окуучу чоңойгондо же чач жасалгасы өзгөргөндө да тааныйт",
                "Маска, көз айнек же кышкы кийимде да тоскоолдуксуз таануу",
                "Сүрөт же телефон экранындагы видео менен алдоого болбойт (Anti-Spoofing)"
            ]
        },
        {
            "id": 6,
            "topic": "06 / ЭЛЕКТРОНДУК ЖУРНАЛ",
            "title": "Автоматташтырылган электрондук журнал жана класстар катышуусу",
            "overview": "Турникеттерден өткөн окуучулардын маалыматтары класстар боюнча бирдиктүү электрондук журналга топтолот. Мугалимдер сабак убактысын үнөмдөшөт.",
            "image": "assets/elektron-jadval-BFo-eBY-.png",
            "imageBadge": "Автоматтык e-Maktab интеграциясы",
            "specs": [
                {
                    "label": "Журнал форматы",
                    "value": "Excel (XLSX), PDF, Онлайн жадыбал"
                },
                {
                    "label": "Каттоо тактыгы",
                    "value": "07:58:12 (секундасына чейин)"
                },
                {
                    "label": "Отчет түрлөрү",
                    "value": "Класс, мектеп, район боюнча"
                },
                {
                    "label": "Интеграция",
                    "value": "e-maktab системасына толук шайкеш"
                }
            ],
            "keyPoints": [
                "Мугалимдерди кагаз иштеринен 100% арылтуу",
                "Окуучулардын сабакка келүү жана кетүү убактысын ачык-айкын каттоо",
                "Мектеп жетекчилиги үчүн бир көз ирмемде жалпы катышууну анализдөө"
            ]
        },
        {
            "id": 7,
            "topic": "07 / АТА-ЭНЕЛЕРГЕ БИЛДИРҮҮЛӨР",
            "title": "Ата-энелерге заматта жетүүчү Telegram жана SMS билдирүүлөрү",
            "overview": "Балаңыз мектепке киргенде жана сабактан чыкканда ата-эненин телефонуна так убактысы жазылган расмий билдирүү келет.",
            "image": "assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg",
            "imageBadge": "Telegram Бот Аркылуу Ыкчам Фотобилдирүү",
            "specs": [
                {
                    "label": "Кабар жеткирүү",
                    "value": "Заматта ата-энеге жетет"
                },
                {
                    "label": "Жеткирүү кепилдиги",
                    "value": "100% ар бир ата-энеге"
                },
                {
                    "label": "Кабар түрлөрү",
                    "value": "Жөнөкөй SMS жана Telegram бот"
                },
                {
                    "label": "Ата-эне үчүн",
                    "value": "Толук тынчтык жана ишеним"
                }
            ],
            "keyPoints": [
                "Ата-эне баласынын мектепке аман-эсен жеткенине толук ынанат",
                "Сабактан кийин мектептен чыккан убактысы да дароо көрсөтүлөт",
                "Ата-эне менен мектеп жетекчилигинин ортосундагы бекем ишеним"
            ]
        },
        {
            "id": 8,
            "topic": "08 / МААЛЫМАТТАР КООПСУЗДУГУ",
            "title": "Окуучулардын маалыматтары толук жана катуу корголгон",
            "overview": "Мектептин жана окуучулардын маалыматтары бөтөн адамдардан корголгон коопсуз системада сакталат. Маалыматтарды мектеп жетекчилиги гана көрө алат.",
            "image": "assets/edavomat-panel-4-Cf-FRJvB.png",
            "imageBadge": "Шифрленген Криптографиялык Коопсуздук Панели",
            "specs": [
                {
                    "label": "Коопсуздук деңгээли",
                    "value": "100% корголгон жана купуя"
                },
                {
                    "label": "Сервер жайгашуусу",
                    "value": "Өзбекстандагы коопсуз серверде"
                },
                {
                    "label": "Кирүү укугу",
                    "value": "Мектеп жетекчилиги үчүн гана"
                },
                {
                    "label": "Ишенимдүүлүк",
                    "value": "Бөтөн адамдар кире албайт"
                }
            ],
            "keyPoints": [
                "Биометрикалык маалыматтар тышкы бөтөн тармактарга чыкпайт",
                "Серверлер Өзбекстан аймагындагы коопсуз маалымат борборлорунда жайгашкан",
                "Тастыкталган мектеп директорлору жана инспекторлор гана кире алышат"
            ]
        },
        {
            "id": 9,
            "topic": "09 / УЛУТТУК ГВАРДИЯ КОРУТУНДУСУ",
            "title": "Системанын мектептерде тартипти жогорулатуудагы практикалык натыйжасы",
            "overview": "Өзбекстан Республикасынын Улуттук Гвардиясынын Сурхандарыя облустук башкармалыгы долбоордун билим сапатына жана коопсуздукка оң таасирин расмий тастыктады.",
            "image": "assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg",
            "imageBadge": "Улуттук Гвардия Кызматкерлери Мене Көзөмөл",
            "specs": [
                {
                    "label": "Жооптуу орган",
                    "value": "Өзбекстан Улуттук Гвардиясы"
                },
                {
                    "label": "Аймак",
                    "value": "Сурхандарыя облусу (Термез шаары)"
                },
                {
                    "label": "Негизги натыйжа",
                    "value": "Сабак калтыруу 74%га кыскарды"
                },
                {
                    "label": "Статус",
                    "value": "Бардык райондордо толук тастыкталган"
                }
            ],
            "keyPoints": [
                "Мектеп аймагына бөтөн адамдардын кириши 100% чектелди",
                "Облус боюнча катышуу көрсөткүчү 98.4%га чейин көтөрүлдү",
                "Долбоор бардык аймактарда киргизүүгө толугу менен сунушталды"
            ]
        }
    ]
};

const PRESENTATION_UI_I18N = {
    "uz": {
        "title": "Rasmiy Tizim Prezentatsiyasi",
        "auto": "AVTO",
        "fullscreen": "TO'LIQ EKRAN",
        "home": "BOSH SAHIFA",
        "specsHeading": "Asosiy Texnik Ko'rsatkichlar:",
        "benefitsHeading": "Asosiy Afzalliklar va Qulayliklar:",
        "prev": "OLDINGI",
        "next": "KEYINGI",
        "dropdownTitle": "Tilni tanlang",
        "shortcuts": "Tugmalar: ← → Slaydlar | Space Avto | Esc Chiqish"
    },
    "en": {
        "title": "Official System Presentation",
        "auto": "AUTO",
        "fullscreen": "FULLSCREEN",
        "home": "HOME",
        "specsHeading": "Key Technical Specifications:",
        "benefitsHeading": "Key Advantages & Features:",
        "prev": "PREVIOUS",
        "next": "NEXT",
        "dropdownTitle": "Select Language",
        "shortcuts": "Keys: ← → Slides | Space Auto | Esc Exit"
    },
    "ru": {
        "title": "Официальная Презентация Системы",
        "auto": "АВТО",
        "fullscreen": "ПОЛНЫЙ ЭКРАН",
        "home": "ГЛАВНАЯ",
        "specsHeading": "Основные Технические Характеристики:",
        "benefitsHeading": "Ключевые Преимущества и Удобства:",
        "prev": "НАЗАД",
        "next": "ВПЕРЕД",
        "dropdownTitle": "Выберите язык",
        "shortcuts": "Клавиши: ← → Слайды | Space Авто | Esc Выход"
    },
    "kz": {
        "title": "Ресми Жүйе Презентациясы",
        "auto": "АВТО",
        "fullscreen": "ТОЛЫҚ ЭКРАН",
        "home": "БАСТЫ БЕТ",
        "specsHeading": "Негізгі Техникалық Көрсеткіштер:",
        "benefitsHeading": "Негізгі Артықшылықтар:",
        "prev": "АРТҚА",
        "next": "АЛҒА",
        "dropdownTitle": "Тілді таңдаңыз",
        "shortcuts": "Пернелер: ← → Слайдтар | Space Авто | Esc Шығу"
    },
    "kg": {
        "title": "Расмий Система Презентациясы",
        "auto": "АВТО",
        "fullscreen": "ТОЛУК ЭКРАН",
        "home": "БАШКЫ БЕТ",
        "specsHeading": "Негизги Техникалык Көрсөткүчтөр:",
        "benefitsHeading": "Негизги Артыкчылыктар:",
        "prev": "АРТКА",
        "next": "АЛГА",
        "dropdownTitle": "Тилди тандаңыз",
        "shortcuts": "Баскычтар: ← → Слайддар | Space Авто | Esc Чыгуу"
    }
};

const LANG_META = {
    'uz': { flag: '🇺🇿', code: 'UZ' },
    'en': { flag: '🇬🇧', code: 'EN' },
    'ru': { flag: '🇷🇺', code: 'RU' },
    'kz': { flag: '🇰🇿', code: 'KZ' },
    'kg': { flag: '🇰🇬', code: 'KG' }
};

class PresentationEngine {
    constructor() {
        this.currentLang = localStorage.getItem('edugate_lang') || 'uz';
        if (!PRESENTATION_SLIDES_I18N[this.currentLang]) {
            this.currentLang = 'uz';
        }
        this.slides = PRESENTATION_SLIDES_I18N[this.currentLang];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.playTimer = null;
        this.slideDuration = 6000;

        this.initDOMElements();
        this.initLanguageSelector();
        this.bindEvents();
        this.renderSlide(0);
        this.updateUILabels(this.currentLang);
    }

    initDOMElements() {
        // Dedicated standalone page elements
        this.pageTopic = document.getElementById('presSlideTopic');
        this.pageTitle = document.getElementById('presSlideTitle');
        this.pageOverview = document.getElementById('presSlideOverview');
        this.pageImage = document.getElementById('presSlideImage');
        this.pageImageBadge = document.getElementById('presSlideImageBadge');
        this.pageSpecsGrid = document.getElementById('presSlideSpecsGrid');
        this.pageKeyPoints = document.getElementById('presSlideKeyPoints');
        this.pageSlideCounter = document.getElementById('presSlideCounter');
        this.pageDotsContainer = document.getElementById('presDots');
        this.pagePrevBtn = document.getElementById('presPrevBtn');
        this.pageNextBtn = document.getElementById('presNextBtn');
        this.pageAutoBtn = document.getElementById('presAutoBtn');
        this.pageFullscreenBtn = document.getElementById('presFullscreenBtn');

        // Modal elements (if on index page)
        this.modal = document.getElementById('presentationModal');
        this.openModalBtns = document.querySelectorAll('[data-open-presentation]');
        this.closeModalBtn = document.getElementById('closePresentationModalBtn');
        this.modalTopic = document.getElementById('presModalTopic');
        this.modalTitle = document.getElementById('presModalTitle');
        this.modalOverview = document.getElementById('presModalOverview');
        this.modalImage = document.getElementById('presModalImage');
        this.modalImageBadge = document.getElementById('presModalImageBadge');
        this.modalSpecsGrid = document.getElementById('presModalSpecsGrid');
        this.modalKeyPoints = document.getElementById('presModalKeyPoints');
        this.modalSlideCounter = document.getElementById('presModalSlideCounter');
        this.modalDotsContainer = document.getElementById('presModalDots');
        this.modalPrevBtn = document.getElementById('presModalPrevBtn');
        this.modalNextBtn = document.getElementById('presModalNextBtn');
        this.modalAutoBtn = document.getElementById('presModalAutoBtn');
        this.modalFullscreenBtn = document.getElementById('presModalFullscreenBtn');

        // Build dots
        this.buildDotChips();
    }

    initLanguageSelector() {
        const trigger = document.getElementById('langDropdownTrigger');
        const menu = document.getElementById('langDropdownMenu');
        const chevron = document.getElementById('langChevron');
        const options = document.querySelectorAll('#customLangDropdown [data-lang-val]');

        if (trigger && menu) {
            const toggleMenu = (e) => {
                e?.stopPropagation();
                const isHidden = menu.classList.contains('hidden');
                if (isHidden) {
                    menu.classList.remove('hidden');
                    chevron?.classList.add('rotate-180');
                } else {
                    menu.classList.add('hidden');
                    chevron?.classList.remove('rotate-180');
                }
            };

            trigger.addEventListener('click', toggleMenu);

            document.addEventListener('click', (e) => {
                if (!menu.contains(e.target) && !trigger.contains(e.target)) {
                    menu.classList.add('hidden');
                    chevron?.classList.remove('rotate-180');
                }
            });
        }

        options.forEach(opt => {
            opt.addEventListener('click', (e) => {
                e.stopPropagation();
                const lang = opt.getAttribute('data-lang-val');
                this.setLanguage(lang);
                if (menu) menu.classList.add('hidden');
                if (chevron) chevron.classList.remove('rotate-180');
            });
        });
    }

    setLanguage(lang) {
        if (!PRESENTATION_SLIDES_I18N[lang]) return;
        this.currentLang = lang;
        localStorage.setItem('edugate_lang', lang);
        this.slides = PRESENTATION_SLIDES_I18N[lang];

        // Update trigger button flag & code
        const meta = LANG_META[lang] || LANG_META['uz'];
        const activeFlag = document.getElementById('activeLangFlag');
        const activeCode = document.getElementById('activeLangCode');
        if (activeFlag) activeFlag.textContent = meta.flag;
        if (activeCode) activeCode.textContent = meta.code;

        // Update active checkmarks in dropdown
        document.querySelectorAll('#customLangDropdown [data-lang-val]').forEach(opt => {
            const check = opt.querySelector('.lang-check');
            if (opt.getAttribute('data-lang-val') === lang) {
                opt.classList.add('bg-cyan-950/70', 'text-cyan-300', 'border-cyan-500/40');
                opt.classList.remove('text-slate-300', 'border-transparent');
                check?.classList.remove('hidden');
            } else {
                opt.classList.remove('bg-cyan-950/70', 'text-cyan-300', 'border-cyan-500/40');
                opt.classList.add('text-slate-300', 'border-transparent');
                check?.classList.add('hidden');
            }
        });

        this.updateUILabels(lang);
        this.buildDotChips();
        this.renderSlide(this.currentIndex);
    }

    updateUILabels(lang) {
        const ui = PRESENTATION_UI_I18N[lang] || PRESENTATION_UI_I18N['uz'];

        // Standalone Page UI elements
        const subtitle = document.getElementById('presTopSubtitle');
        if (subtitle) subtitle.textContent = ui.title;

        const autoLabel = document.getElementById('presAutoLabel');
        if (autoLabel) autoLabel.textContent = ui.auto;

        const fullLabel = document.getElementById('presFullscreenLabel');
        if (fullLabel) fullLabel.textContent = ui.fullscreen;

        const homeLabel = document.getElementById('presHomeLabel');
        if (homeLabel) homeLabel.textContent = ui.home;

        const specsHeading = document.getElementById('presSpecsHeading');
        if (specsHeading) specsHeading.textContent = ui.specsHeading;

        const benefitsHeading = document.getElementById('presBenefitsHeading');
        if (benefitsHeading) benefitsHeading.textContent = ui.benefitsHeading;

        const prevLabel = document.getElementById('presPrevLabel');
        if (prevLabel) prevLabel.textContent = ui.prev;

        const nextLabel = document.getElementById('presNextLabel');
        if (nextLabel) nextLabel.textContent = ui.next;

        const dropdownTitle = document.getElementById('langDropdownTitle');
        if (dropdownTitle) dropdownTitle.textContent = ui.dropdownTitle;

        const shortcuts = document.getElementById('presShortcutsHint');
        if (shortcuts) shortcuts.textContent = ui.shortcuts;

        // Modal Page UI elements (if open on index)
        const modalAutoSpan = this.modalAutoBtn?.querySelector('span');
        if (modalAutoSpan) modalAutoSpan.textContent = ui.auto;

        const modalPrevSpan = this.modalPrevBtn?.querySelector('span');
        if (modalPrevSpan) modalPrevSpan.textContent = ui.prev;

        const modalNextSpan = this.modalNextBtn?.querySelector('span');
        if (modalNextSpan) modalNextSpan.textContent = ui.next;
    }

    buildDotChips() {
        const renderDots = (container) => {
            if (!container) return;
            container.innerHTML = '';
            this.slides.forEach((slide, idx) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `pres-dot px-3 py-1 rounded-lg text-xs font-mono font-bold transition ${
                    idx === this.currentIndex
                        ? 'bg-cyan-500 text-white shadow-[0_0_10px_rgba(6,182,212,0.7)]'
                        : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700'
                }`;
                btn.textContent = `0${slide.id}`;
                btn.title = slide.title;
                btn.addEventListener('click', () => {
                    this.goToSlide(idx);
                });
                container.appendChild(btn);
            });
        };

        renderDots(this.pageDotsContainer);
        renderDots(this.modalDotsContainer);
    }

    bindEvents() {
        // Dedicated page buttons
        if (this.pagePrevBtn) this.pagePrevBtn.addEventListener('click', () => this.prevSlide());
        if (this.pageNextBtn) this.pageNextBtn.addEventListener('click', () => this.nextSlide());
        if (this.pageAutoBtn) this.pageAutoBtn.addEventListener('click', () => this.toggleAutoPlay());
        if (this.pageFullscreenBtn) this.pageFullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

        // Modal buttons
        if (this.modalPrevBtn) this.modalPrevBtn.addEventListener('click', () => this.prevSlide());
        if (this.modalNextBtn) this.modalNextBtn.addEventListener('click', () => this.nextSlide());
        if (this.modalAutoBtn) this.modalAutoBtn.addEventListener('click', () => this.toggleAutoPlay());
        if (this.modalFullscreenBtn) this.modalFullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeModal());
        }

        // Open modal triggers from landing page
        this.openModalBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal();
            });
        });

        // Global keyboard listeners
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') {
                this.nextSlide();
            } else if (e.key === 'ArrowLeft') {
                this.prevSlide();
            } else if (e.key === ' ') {
                e.preventDefault();
                this.toggleAutoPlay();
            } else if (e.key.toLowerCase() === 'f') {
                this.toggleFullscreen();
            } else if (e.key === 'Escape') {
                if (this.modal && !this.modal.classList.contains('hidden')) {
                    this.closeModal();
                } else if (window.location.pathname.includes('presentation')) {
                    window.location.href = '/edugate/';
                }
            }
        });
    }

    renderSlide(index) {
        if (index < 0) index = this.slides.length - 1;
        if (index >= this.slides.length) index = 0;
        this.currentIndex = index;

        const slide = this.slides[index];

        const updateContent = (elements) => {
            if (!elements.topic) return;

            elements.topic.textContent = slide.topic;
            elements.title.textContent = slide.title;
            elements.overview.textContent = slide.overview;

            if (elements.image) {
                elements.image.src = slide.image;
                elements.image.alt = slide.title;
            }

            if (elements.imageBadge) {
                elements.imageBadge.textContent = slide.imageBadge;
            }

            if (elements.slideCounter) {
                elements.slideCounter.textContent = `${slide.id} / ${this.slides.length}`;
            }

            // Specs grid
            if (elements.specsGrid) {
                elements.specsGrid.innerHTML = slide.specs.map(spec => `
                    <div class="p-3 bg-[#0B132B] rounded-xl border border-slate-800 shadow-md">
                        <span class="text-[10px] uppercase text-slate-400 font-mono block">${spec.label}</span>
                        <h5 class="text-xs sm:text-sm font-bold text-cyan-300 mt-1">${spec.value}</h5>
                    </div>
                `).join('');
            }

            // Key Points
            if (elements.keyPoints) {
                elements.keyPoints.innerHTML = slide.keyPoints.map(point => `
                    <li class="flex items-start gap-2 text-xs sm:text-[13px] text-slate-300">
                        <i class="fas fa-check-circle text-emerald-400 text-xs mt-1 shrink-0"></i>
                        <span>${point}</span>
                    </li>
                `).join('');
            }
        };

        // Update dedicated page elements
        updateContent({
            topic: this.pageTopic,
            title: this.pageTitle,
            overview: this.pageOverview,
            image: this.pageImage,
            imageBadge: this.pageImageBadge,
            slideCounter: this.pageSlideCounter,
            specsGrid: this.pageSpecsGrid,
            keyPoints: this.pageKeyPoints
        });

        // Update modal elements
        updateContent({
            topic: this.modalTopic,
            title: this.modalTitle,
            overview: this.modalOverview,
            image: this.modalImage,
            imageBadge: this.modalImageBadge,
            slideCounter: this.modalSlideCounter,
            specsGrid: this.modalSpecsGrid,
            keyPoints: this.modalKeyPoints
        });

        // Update active dot indicators
        this.updateActiveDots();
    }

    updateActiveDots() {
        const update = (container) => {
            if (!container) return;
            const buttons = container.querySelectorAll('button');
            buttons.forEach((btn, idx) => {
                if (idx === this.currentIndex) {
                    btn.className = 'pres-dot px-3 py-1 rounded-lg text-xs font-mono font-bold transition bg-cyan-500 text-white shadow-[0_0_10px_rgba(6,182,212,0.7)]';
                } else {
                    btn.className = 'pres-dot px-3 py-1 rounded-lg text-xs font-mono font-bold transition bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700';
                }
            });
        };

        update(this.pageDotsContainer);
        update(this.modalDotsContainer);
    }

    goToSlide(index) {
        this.renderSlide(index);
        if (this.isPlaying) {
            this.restartAutoPlay();
        }
    }

    nextSlide() {
        this.goToSlide(this.currentIndex + 1);
    }

    prevSlide() {
        this.goToSlide(this.currentIndex - 1);
    }

    toggleAutoPlay() {
        this.isPlaying = !this.isPlaying;
        
        const updateBtn = (btn) => {
            if (!btn) return;
            const icon = btn.querySelector('i');
            const span = btn.querySelector('span');
            const ui = PRESENTATION_UI_I18N[this.currentLang] || PRESENTATION_UI_I18N['uz'];

            if (this.isPlaying) {
                if (icon) icon.className = 'fas fa-pause text-[10px] text-amber-400 animate-pulse';
                if (span) span.textContent = 'PAUZA';
                btn.classList.add('border-amber-400/50', 'text-amber-300');
            } else {
                if (icon) icon.className = 'fas fa-play text-[10px]';
                if (span) span.textContent = ui.auto;
                btn.classList.remove('border-amber-400/50', 'text-amber-300');
            }
        };

        updateBtn(this.pageAutoBtn);
        updateBtn(this.modalAutoBtn);

        if (this.isPlaying) {
            this.startAutoPlay();
        } else {
            this.stopAutoPlay();
        }
    }

    startAutoPlay() {
        this.stopAutoPlay();
        this.playTimer = setInterval(() => {
            this.nextSlide();
        }, this.slideDuration);
    }

    stopAutoPlay() {
        if (this.playTimer) {
            clearInterval(this.playTimer);
            this.playTimer = null;
        }
    }

    restartAutoPlay() {
        this.stopAutoPlay();
        this.startAutoPlay();
    }

    openModal() {
        if (!this.modal) return;
        this.modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        this.renderSlide(this.currentIndex);
    }

    closeModal() {
        if (!this.modal) return;
        this.modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        if (this.isPlaying) {
            this.toggleAutoPlay();
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            } else if (document.documentElement.webkitRequestFullscreen) {
                document.documentElement.webkitRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        }
    }

    initStandaloneMode() {
        this.setLanguage(this.currentLang);
        this.renderSlide(0);
    }
}

// Initialize Presentation Engine
document.addEventListener('DOMContentLoaded', () => {
    window.edugatePresentation = new PresentationEngine();
});
