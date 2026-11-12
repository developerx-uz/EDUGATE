from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_phone_request_kb() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish klaviaturasi"""
    btn = KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)
    return ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True, one_time_keyboard=True)

def get_parent_main_menu() -> ReplyKeyboardMarkup:
    """Ota-onaning asosiy menyusi"""
    kbs = [
        [KeyboardButton(text="📊 Bugungi Davomat"), KeyboardButton(text="🗓 Oylik Hisobot")],
        [KeyboardButton(text="📝 Sababli Dars Qoldirish (Ariza)"), KeyboardButton(text="👨‍👩‍👧 Farzandlarim")],
        [KeyboardButton(text="🏫 Maktab Ma'muriyati"), KeyboardButton(text="⚙️ Sozlamalar & Yordam")]
    ]
    return ReplyKeyboardMarkup(keyboard=kbs, resize_keyboard=True)

def get_admin_main_menu() -> ReplyKeyboardMarkup:
    """Maktab direktori / Milliy gvardiya inspektori menyusi"""
    kbs = [
        [KeyboardButton(text="🚨 Jonli Maktab Monitoringi"), KeyboardButton(text="⚠️ Kechikkanlar Ro'yxati")],
        [KeyboardButton(text="🛑 Begona Shaxslar Urinishi"), KeyboardButton(text="📞 Tezkor Favqulodda Qo'ng'iroq")],
        [KeyboardButton(text="📈 Tuman & Viloyat Reytingi")]
    ]
    return ReplyKeyboardMarkup(keyboard=kbs, resize_keyboard=True)

def get_order_inline_kb() -> InlineKeyboardMarkup:
    """Turniket & Kamera buyurtma klaviaturasi"""
    kb = [
        [InlineKeyboardButton(text="🛒 Turniket Uskunalariga Buyurtma Berish", callback_data="order_equipment")],
        [InlineKeyboardButton(text="🌐 Veb-portalga o'tish (EDUGATE)", url="https://developerx.uz/edugate/")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_children_inline_kb(children: list) -> InlineKeyboardMarkup:
    """Farzandlar ro'yxati inline menyusi"""
    buttons = []
    for c in children:
        name = c.get('full_name') or f"{c.get('first_name')} {c.get('last_name')}"
        buttons.append([InlineKeyboardButton(text=f"👤 {name} ({c.get('class_name', '')})", callback_data=f"child_{c.get('id')}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
