# EDUGATE Tizimi — Arxitektura va Texnik Qo'llanma

## Arxitektura Tamoyillari
1. **Separation of Concerns (Vazifalarni ajratish):** Kamera va apparatlar biznes-mantiqni bilmaydi. Bot faqat xabarnomani foydalanuvchiga yetkazadi. Barcha mantiq `backend` yadroda bajariladi.
2. **Debounce (Anti-Spam):** O'quvchi kamera oldida uzoq tursa, tizim takroriy xabarlarni avtomatik bloklaydi.
3. **Multi-Tenant Ready:** Tizim bir nechta maktabni bitta bazada boshqarishga mo'ljallangan (`school_id`).
4. **Offline Resiliency:** Kameralar internet uzilganda o'zida saqlab, internet kelganda to'plam tarzida uzatishi mumkin.
