[#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import sqlite3
import logging
import hashlib
import threading
import time
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

TOKEN = "7846066465:AAHmbmBoILA0aw1gcNfgcabY7-Y5Nse2faQ"
ADMIN_ID = 123456789  # GANTI DENGAN ID TELEGRAM ANDA
DB_PATH = "avg_premium.db"
HEADER_IMAGE_URL = "https://i.imgur.com/your-image.png"

PAYMENT_METHODS = {"DANA": "08123456789", "GOPAY": "08123456789", "OVO": "08123456789"}
PRICE_LIST = {
    '1': 15000, '2': 25000, '3': 35000, '4': 45000, '5': 55000,
    '6': 65000, '7': 75000, '8': 85000, '9': 95000, '10': 105000,
    '12': 120000, 'permanent': 200000
}
PACKAGE_NAMES = {
    '1': '1 Bulan', '2': '2 Bulan', '3': '3 Bulan', '4': '4 Bulan',
    '5': '5 Bulan', '6': '6 Bulan', '7': '7 Bulan', '8': '8 Bulan',
    '9': '9 Bulan', '10': '10 Bulan', '12': '1 Tahun', 'permanent': 'Permanen'
}
MAINTENANCE_DURATION = 60

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        premium_expiry TEXT,
        energy INTEGER DEFAULT 0,
        registered_at TEXT,
        license_key TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package TEXT,
        amount INTEGER,
        payment_method TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        completed_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_id TEXT,
        phone_info TEXT,
        last_seen TEXT,
        is_active INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at) VALUES (?, ?, ?, ?)",
              (user_id, username, full_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def set_premium(user_id, months):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if months == 'permanent':
        expiry = '2099-12-31T23:59:59'
    else:
        expiry = (datetime.now() + timedelta(days=30*int(months))).isoformat()
    license_key = hashlib.sha256(f"{user_id}{expiry}AVG_SECRET".encode()).hexdigest()[:20]
    c.execute("UPDATE users SET premium_expiry = ?, license_key = ? WHERE user_id = ?", (expiry, license_key, user_id))
    c.execute("UPDATE users SET energy = energy + 1000 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return expiry, license_key

def is_premium(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT premium_expiry FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        try:
            if row[0] == '2099-12-31T23:59:59':
                return True
            return datetime.now() < datetime.fromisoformat(row[0])
        except:
            return False
    return False

def log_transaction(user_id, package, amount, payment_method='', status='pending'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, package, amount, payment_method, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, package, amount, payment_method, status, datetime.now().isoformat()))
    trans_id = c.lastrowid
    conn.commit()
    conn.close()
    return trans_id

def update_transaction_status(trans_id, status, completed_at=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if completed_at is None:
        completed_at = datetime.now().isoformat()
    c.execute("UPDATE transactions SET status = ?, completed_at = ? WHERE id = ?", (status, completed_at, trans_id))
    conn.commit()
    conn.close()

def get_transaction(trans_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username, full_name, premium_expiry, energy FROM users ORDER BY registered_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

class MaintenanceManager:
    def __init__(self):
        self.is_maintenance = False
        self.maintenance_until = None
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self._thread.start()

    def _maintenance_loop(self):
        while not self._stop_event.is_set():
            if not self.is_maintenance:
                if random.random() < 0.05:
                    self._start_maintenance()
            else:
                if datetime.now() >= self.maintenance_until:
                    self._end_maintenance()
            time.sleep(30)

    def _start_maintenance(self):
        self.is_maintenance = True
        self.maintenance_until = datetime.now() + timedelta(seconds=MAINTENANCE_DURATION)
        logger.info(f"Maintenance started until {self.maintenance_until}")

    def _end_maintenance(self):
        self.is_maintenance = False
        self.maintenance_until = None
        logger.info("Maintenance finished")

    def is_under_maintenance(self):
        return self.is_maintenance

    def get_maintenance_time_left(self):
        if self.is_maintenance and self.maintenance_until:
            left = (self.maintenance_until - datetime.now()).total_seconds()
            return max(0, int(left))
        return 0

maintenance_manager = MaintenanceManager()

def check_maintenance(func):
    async def wrapper(update, context, *args, **kwargs):
        if maintenance_manager.is_under_maintenance():
            await update.message.reply_text(
                f"🛠️ Bot sedang maintenance\\n⏳ Waktu tersisa: {maintenance_manager.get_maintenance_time_left()} detik\\nMohon tunggu sebentar.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("🛒 Beli Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("📊 Cek Status", callback_data="status")],
        [InlineKeyboardButton("⚡ Tambah Energi", callback_data="add_energy")],
        [InlineKeyboardButton("📖 Testimoni", callback_data="testimoni")],
        [InlineKeyboardButton("👤 Kontak Developer", callback_data="contact")]
    ]
    return InlineKeyboardMarkup(buttons)

def package_keyboard():
    buttons = []
    for i in range(1, 11):
        label = f"{i} Bulan - Rp {PRICE_LIST[str(i)]:,}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"buy_{i}")])
    buttons.append([InlineKeyboardButton("1 Tahun - Rp 120.000", callback_data="buy_12")])
    buttons.append([InlineKeyboardButton("🌟 Permanen - Rp 200.000", callback_data="buy_permanent")])
    buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def payment_keyboard(trans_id):
    buttons = [
        [InlineKeyboardButton("✅ Saya Sudah Transfer", callback_data=f"confirm_payment_{trans_id}")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(buttons)

def admin_confirm_keyboard(trans_id, user_id):
    buttons = [
        [InlineKeyboardButton("✅ Done (Aktivasi)", callback_data=f"admin_done_{trans_id}_{user_id}")],
        [InlineKeyboardButton("❌ Belum (Tolak)", callback_data=f"admin_reject_{trans_id}_{user_id}")]
    ]
    return InlineKeyboardMarkup(buttons)

@check_maintenance
async def start(update, context):
    user = update.effective_user
    add_user(user.id, user.username, user.full_name)
    caption = (
        "╔═══════════════════════════════════════╗\\n"
        "║   🤖 AVG SPACE – PREMIUM BOT         ║\\n"
        "╠═══════════════════════════════════════╣\\n"
        f"║  Selamat datang, {user.first_name}!   ║\\n"
        "║                                       ║\\n"
        "║  Gunakan menu di bawah untuk mulai.   ║\\n"
        "╚═══════════════════════════════════════╝"
    )
    try:
        await update.message.reply_photo(photo=HEADER_IMAGE_URL, caption=caption, reply_markup=main_menu_keyboard())
    except:
        await update.message.reply_text(caption, reply_markup=main_menu_keyboard())

@check_maintenance
async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "buy_premium":
        await query.edit_message_text("🛒 *Pilih Paket Premium:*", parse_mode=ParseMode.MARKDOWN, reply_markup=package_keyboard())
    elif data.startswith("buy_"):
        package = data.split("_")[1]
        await show_checkout(update, context, package)
    elif data == "status":
        await status(update, context)
    elif data == "add_energy":
        await add_energy_user(update, context)
    elif data == "testimoni":
        await testimoni(update, context)
    elif data == "contact":
        await contact(update, context)
    elif data.startswith("confirm_payment_"):
        trans_id = int(data.split("_")[2])
        await confirm_payment(update, context, trans_id)
    elif data.startswith("admin_done_"):
        parts = data.split("_")
        trans_id = int(parts[2])
        user_id_target = int(parts[3])
        await admin_done(update, context, trans_id, user_id_target)
    elif data.startswith("admin_reject_"):
        parts = data.split("_")
        trans_id = int(parts[2])
        user_id_target = int(parts[3])
        await admin_reject(update, context, trans_id, user_id_target)
    elif data == "back_main":
        caption = "🔙 Kembali ke menu utama."
        try:
            await query.edit_message_media(media=InputFile(HEADER_IMAGE_URL), caption=caption, reply_markup=main_menu_keyboard())
        except:
            await query.edit_message_text(caption, reply_markup=main_menu_keyboard())
    else:
        await query.edit_message_text("❌ Perintah tidak dikenali.", reply_markup=main_menu_keyboard())

async def show_checkout(update, context, package):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    price = PRICE_LIST[package]
    package_name = PACKAGE_NAMES[package]
    trans_id = log_transaction(user_id, package, price, status='pending')
    payment_text = "\\n".join([f"• {method}: {number}" for method, number in PAYMENT_METHODS.items()])
    struk = f"""
╔═══════════════════════════════════════╗
║          🧾 STRUK PEMBELIAN           ║
╠═══════════════════════════════════════╣
║  🛒 Paket: {package_name}
║  💰 Harga: Rp {price:,}
║  📅 Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}
║  🆔 Transaksi: #{trans_id}
╠═══════════════════════════════════════╣
║  Silakan transfer ke salah satu:      ║
{payment_text}
║                                       ║
║  Setelah transfer, klik tombol di     ║
║  bawah untuk konfirmasi.              ║
╚═══════════════════════════════════════╝
"""
    await query.edit_message_text(struk, parse_mode=ParseMode.MARKDOWN, reply_markup=payment_keyboard(trans_id))

async def confirm_payment(update, context, trans_id):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    trans = get_transaction(trans_id)
    if not trans:
        await query.edit_message_text("❌ Transaksi tidak ditemukan.", reply_markup=main_menu_keyboard())
        return
    admin_text = f"""
🔔 *KONFIRMASI PEMBAYARAN*
👤 User: {user.first_name} (@{user.username or 'no username'})
🆔 ID: {user.id}
📦 Paket: {PACKAGE_NAMES[trans[2]]}
💰 Harga: Rp {trans[3]:,}
📌 Status: Menunggu konfirmasi admin
"""
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_confirm_keyboard(trans_id, user.id)
    )
    await query.edit_message_text(
        "✅ Konfirmasi terkirim! Tunggu aktivasi dari admin.\\nJika belum diaktivasi dalam 1x24 jam, hubungi admin.",
        reply_markup=main_menu_keyboard()
    )

async def admin_done(update, context, trans_id, user_id_target):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ Anda bukan admin!")
        return
    trans = get_transaction(trans_id)
    if not trans:
        await query.edit_message_text("❌ Transaksi tidak ditemukan.")
        return
    package = trans[2]
    expiry, license_key = set_premium(user_id_target, package)
    update_transaction_status(trans_id, 'completed')
    struk_done = f"""
╔═══════════════════════════════════════╗
║      🎉 PEMBAYARAN BERHASIL! 🎉      ║
╠═══════════════════════════════════════╣
║  🛒 Paket: {PACKAGE_NAMES[package]}
║  💰 Harga: Rp {trans[3]:,}
║  📅 Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}
║  🆔 Transaksi: #{trans_id}
╠═══════════════════════════════════════╣
║  ✅ Premium AKTIF!
║  📆 Berakhir: {expiry}
║  🔑 Lisensi: `{license_key}`
║  ⚡ Bonus Energi: 1000
║                                       ║
║  Masukkan lisensi di aplikasi AVG     ║
║  SPACE untuk unlock premium.         ║
╚═══════════════════════════════════════╝
"""
    try:
        await context.bot.send_message(chat_id=user_id_target, text=struk_done, parse_mode=ParseMode.MARKDOWN)
    except:
        pass
    await query.edit_message_text(
        f"✅ Premium telah diaktivasi untuk user {user_id_target}.\\n📦 Paket: {PACKAGE_NAMES[package]}\\n📆 Berakhir: {expiry}\\n🔑 Lisensi: `{license_key}`",
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_reject(update, context, trans_id, user_id_target):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ Anda bukan admin!")
        return
    update_transaction_status(trans_id, 'rejected')
    try:
        await context.bot.send_message(
            chat_id=user_id_target,
            text="❌ *Pembayaran ditolak*\\n\\nSilakan cek kembali transfer Anda atau hubungi admin.",
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass
    await query.edit_message_text(f"❌ Transaksi #{trans_id} ditolak.")

async def status(update, context):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.callback_query.edit_message_text("Anda belum terdaftar. Kirim /start.", reply_markup=main_menu_keyboard())
        return
    premium = is_premium(user_id)
    expiry = user[3] if user[3] else "Tidak ada"
    license_key = user[6] if user[6] else "Belum"
    text = f"""
╔═══════════════════════════════════════╗
║        📊 STATUS AKUN                 ║
╠═══════════════════════════════════════╣
║  Premium: {'✅ Aktif' if premium else '❌ Tidak aktif'}
║  Berakhir: {expiry}
║  Energi: ⚡ {user[4] if user[4] else 0}
║  Lisensi: `{license_key}`
║                                       ║
║  Beli premium: /buy
║  Hubungi owner: @kiyyofficial
╚═══════════════════════════════════════╝
"""
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard())

async def add_energy_user(update, context):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET energy = energy + 10 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    await update.callback_query.edit_message_text("⚡ +10 Energi telah ditambahkan ke akun Anda!", reply_markup=main_menu_keyboard())

async def testimoni(update, context):
    testimonials = [
        "🌟 AVG SPACE benar-benar mengubah pengalaman gaming saya! – Andi",
        "🔥 Premium worth it! Energi unlimited! – Budi",
        "💯 Pelayanan cepat, harga terjangkau. – Cinta",
        "🚀 Setelah pakai AVG SPACE, FPS naik 2x! – Dani",
        "⭐ Admin ramah, proses aktivasi cepat. – Eka"
    ]
    testimonial = random.choice(testimonials)
    await update.callback_query.edit_message_text(
        f"📖 *Testimoni Pengguna AVG SPACE*\\n\\n{testimonial}\\n\\n✨ Bergabunglah dengan ribuan gamer!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard()
    )

async def contact(update, context):
    text = """
👤 *Kontak Developer*

📱 WhatsApp: 6285746399596
✈️ Telegram: @kiyyofficial
🤖 Bot: @AVG_SPACE_BOT
"""
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard())

@check_maintenance
async def add_premium_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Format: /addpremium <user_id> <bulan> (1-12, permanent)")
            return
        user_id = int(args[0])
        months = args[1]
        expiry, license = set_premium(user_id, months)
        await update.message.reply_text(f"✅ Premium {months} bulan diberikan ke user {user_id}. Lisensi: {license}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@check_maintenance
async def list_users_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("Belum ada user terdaftar.")
        return
    text = "📋 *Daftar User AVG SPACE*\\n\\n"
    for u in users:
        premium = "✅ Premium" if u[3] and (u[3] == '2099-12-31T23:59:59' or datetime.now() < datetime.fromisoformat(u[3])) else "❌ Free"
        text += f"ID: {u[0]} | {u[1] or u[2] or '-'} | {premium} | Energi: {u[4]}\\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@check_maintenance
async def check_user_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    try:
        user_id = int(context.args[0]) if context.args else None
        if not user_id:
            await update.message.reply_text("Format: /check <user_id>")
            return
        user = get_user(user_id)
        if not user:
            await update.message.reply_text(f"User {user_id} tidak ditemukan.")
            return
        premium = is_premium(user_id)
        energy = user[4] if user[4] else 0
        text = f"""
🆔 User ID: {user[0]}
👤 Username: {user[1] or '-'}
📛 Nama: {user[2] or '-'}
📅 Premium: {'Aktif' if premium else 'Tidak aktif'}
⏳ Expiry: {user[3] or '-'}
⚡ Energi: {energy}
🔑 Lisensi: {user[6] or '-'}
📆 Terdaftar: {user[5] or '-'}
"""
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@check_maintenance
async def add_energy_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
]
