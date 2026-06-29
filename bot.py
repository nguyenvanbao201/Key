from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from database import *
from key import *

bot = TeleBot(TOKEN)

# ===========================
# MENU CHÍNH
# ===========================

@bot.message_handler(commands=['start'])
def start(message):
    users = get_users()

    if str(message.chat.id) not in users:
        users[str(message.chat.id)] = {
            "id": message.chat.id,
            "name": message.from_user.first_name,
            "username": message.from_user.username
        }
        save_users(users)

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🎮 VUA THOÁT HIỂM (AUTO)", callback_data="tool_vth"),
        InlineKeyboardButton("🏎 CHẠY ĐUA TỐC ĐỘ", callback_data="tool_cdtd"),
        InlineKeyboardButton("🎲 LOTTO (AUTO)", callback_data="tool_lotto")
    )

    bot.send_message(
        message.chat.id,
        "🎉 <b>SHOP KEY TOOL</b>\n\nChọn tool muốn mua:",
        parse_mode="HTML",
        reply_markup=kb
    )

# ===========================
# CHỌN TOOL
# ===========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tool_"))
def choose_tool(call):
    tool = call.data.split("_")[1]

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("3 ngày - 4.000đ", callback_data=f"buy_{tool}_3"),
        InlineKeyboardButton("7 ngày - 10.000đ", callback_data=f"buy_{tool}_7"),
        InlineKeyboardButton("30 ngày - 20.000đ", callback_data=f"buy_{tool}_30"),
        InlineKeyboardButton("60 ngày - 40.000đ", callback_data=f"buy_{tool}_60")
    )

    bot.edit_message_text(
        f"📦 {PRICES[tool]['name']}\n\nChọn thời hạn sử dụng:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

# ===========================
# TẠO ĐƠN
# ===========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy(call):
    _, tool, day = call.data.split("_")
    uid = str(call.from_user.id)

    orders = get_orders()

    # ❌ Không cho tạo đơn mới nếu đơn cũ chưa xong
    if uid in orders:
        status = orders[uid].get("status")
        if status not in ["done", "reject"]:
            bot.answer_callback_query(call.id, "❌ Bạn đang có đơn chưa xử lý!", show_alert=True)
            return

    price = PRICES[tool][day]
    payment_code = f"{tool.upper()}-{day}D-{uid}"

    orders[uid] = {
        "tool": tool,
        "day": day,
        "price": price,
        "payment_code": payment_code,
        "status": "pending"
    }

    save_orders(orders)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Tôi đã chuyển khoản", callback_data="paid"))

    bot.edit_message_text(
        f"""💳 THÔNG TIN THANH TOÁN

🏦 Ngân hàng: {BANK_NAME}

💳 STK:
{ACCOUNT_NUMBER}

👤 Chủ TK:
{ACCOUNT_NAME}

💰 Số tiền:
{price:,} VNĐ

📝 Nội dung:
{payment_code}

Sau khi chuyển khoản hãy bấm nút bên dưới.
""",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

# ===========================
# XÁC NHẬN THANH TOÁN
# ===========================

@bot.callback_query_handler(func=lambda call: call.data == "paid")
def paid(call):
    orders = get_orders()
    uid = str(call.from_user.id)

    # ❌ Không có đơn
    if uid not in orders:
        bot.answer_callback_query(call.id, "❌ Không tìm thấy đơn!", show_alert=True)
        return

    status = orders[uid].get("status")

    # ❌ Đã xử lý → chặn
    if status in ["done", "reject"]:
        bot.answer_callback_query(call.id, "❌ Đơn này đã xử lý rồi!\nTạo đơn mới nhé.", show_alert=True)
        return

    # ❌ Đã bấm rồi → không cho spam
    if status == "waiting":
        bot.answer_callback_query(call.id, "⏳ Bạn đã gửi rồi, vui lòng chờ admin!", show_alert=True)
        return

    # ✅ Đánh dấu đã gửi admin
    orders[uid]["status"] = "waiting"
    save_orders(orders)

    bot.answer_callback_query(call.id, "✅ Đã gửi cho admin!")

    username = f"@{call.from_user.username}" if call.from_user.username else "Không có"

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_{uid}"),
        InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_{uid}")
    )

    bot.send_message(
        ADMIN_ID,
        f"""🔔 ĐƠN HÀNG MỚI

👤 Người mua: {call.from_user.first_name}
👤 Username: {username}
🆔 ID: {call.from_user.id}

📦 Tool: {PRICES[orders[uid]["tool"]]["name"]}
📅 Gói: {orders[uid]['day']} ngày

💰 Giá: {orders[uid]['price']:,} VNĐ

📝 Nội dung CK:
{orders[uid]['payment_code']}
""",
        reply_markup=kb
    )

# ===========================
# DUYỆT
# ===========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Không có quyền!")
        return

    uid = call.data.split("_")[1]
    orders = get_orders()

    if uid not in orders:
        return

    tool = orders[uid]["tool"]
    day = orders[uid]["day"]

    key = create_key(tool)
    expire = get_expire(day)
    
    # ===== Lưu key vào license.json =====
import json

try:
    with open("license.json", "r", encoding="utf-8") as f:
        db = json.load(f)
except:
    db = {}

db[key] = {
    "tool": tool,
    "expire": expire,
    "hwid": "",
    "status": "active"
}

with open("license.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=4, ensure_ascii=False)
# ===== Kết thúc =====

    bot.send_message(
        uid,
        f"""🎉 Thanh toán thành công!

🔑 Key:
{key}

📅 Hết hạn:
{expire}
"""
    )

    orders[uid]["status"] = "done"
    save_orders(orders)

    bot.edit_message_text("✅ Đã duyệt và gửi key.", call.message.chat.id, call.message.message_id)

# ===========================
# TỪ CHỐI
# ===========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Không có quyền!")
        return

    uid = call.data.split("_")[1]
    orders = get_orders()

    if uid in orders:
        orders[uid]["status"] = "reject"
        save_orders(orders)

    bot.send_message(uid, "❌ Đơn hàng bị từ chối.")
    bot.edit_message_text("❌ Đã từ chối.", call.message.chat.id, call.message.message_id)

# ===========================
# RUN
# ===========================

print("Bot đang chạy...")
bot.infinity_polling(skip_pending=True)