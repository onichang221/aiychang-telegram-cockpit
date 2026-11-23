"""
app.py — Universal Telegram Remote Cockpit & Brain Dump Engine (Render & Cloud Ready)
Supports both Render Webhook (24/7 Cloud) and Local Long Polling with zero external dependencies.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import threading
import time

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
PORT = int(os.environ.get("PORT", "10000"))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "").strip()

# Local storage fallback (or in-memory / cloud repo)
DUMPS_STORE = []

def send_telegram_message(chat_id, text, reply_markup=None):
    if not TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN missing")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return None

def get_keyboard():
    return {
        "keyboard": [
            [{"text": "🎯 ຂໍສະຫຼຸບດ່ວນ"}, {"text": "📊 ສະຖານະ OS"}],
            [{"text": "🧠 Brain Dump (ເທຄວາມຄິດ)"}, {"text": "🧠 ກວດ SOP-04"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def process_brain_dump(raw_text):
    now = datetime.now()
    date_display = now.strftime("%Y-%m-%d %H:%M")
    
    DUMPS_STORE.append({"time": date_display, "text": raw_text})
    total_count = len(DUMPS_STORE)
    
    text_lower = raw_text.lower()
    positive_words = ["ຂອບໃຈ", "ສູ້", "ດີໃຈ", "ດີ", "ງ່າຍ", "ອີຊີ", "ເກັ່ງ", "ພູມໃຈ", "ຮັກ"]
    tired_words = ["ເມື່ອຍ", "ນອນບໍ່ຫຼັບ", "ວຸ້ນວາຍ", "ຄຽດ", "ຄິດຫຼາຍ", "ກັງວົນ", "ແນ່ນໜ້າເອິກ", "ບໍ່ມີແຮງ", "ຕັນ", "ຢ້ານ"]
    workload_words = ["ວຽກຫຼາຍ", "ບໍ່ທັນ", "ກຳນົດ", "ລູກຄ້າ", "ໂປຣເຈັກ", "ເງິນ", "ຄົນ", "ທີມ", "ຂາຍ"]
    
    detected_emotions = []
    if any(w in text_lower for w in positive_words):
        detected_emotions.append("ຄວາມພູມໃຈໃນຕົວເອງ / ກຳລັງໃຈຟື້ນຟູ & ເຫັນເສັ້ນທາງຊັດເຈນ")
    if any(w in text_lower for w in tired_words):
        detected_emotions.append("ສະໝອງກຳລັງແບກ Cognitive Overload / ມີຄວາມເມື່ອຍລ້າສະສົມ")
    if any(w in text_lower for w in workload_words):
        detected_emotions.append("ຄວາມກັງວົນເລື່ອງສາຍພານງານ ແລະ ຄວາມຮັບຜິດຊອບ")
    if not detected_emotions:
        detected_emotions.append("ຄວາມຄິດແລ່ນໄວ ແລະ ກຳລັງທົບທວນຊີວິດ/ບົດຮຽນ")
        
    sentences = [s.strip() for s in re.split(r'[\n\.\,\!\?]+', raw_text) if len(s.strip()) > 3]
    control_items = []
    let_go_items = []
    for s in sentences:
        s_low = s.lower()
        if any(w in s_low for w in ["ຂ້ອຍ", "ເຮົາ", "ຈະ", "ຕ້ອງ", "ລົງມື", "ທັກ", "ຂຽນ", "ຕັດ", "ກວດ", "ນອນ", "ພັກ", "ສູ້", "ຊ້ອມ"]):
            if len(control_items) < 3:
                control_items.append(s)
        else:
            if len(let_go_items) < 3:
                let_go_items.append(s)
                
    if not control_items:
        control_items.append("ຮັກສາຈັງຫວະນີ້ໄວ້ ➔ ພັກຜ່ອນ ➔ ໃຫ້ລາງວັນຕົວເອງ ➔ ລຸຍຕໍ່ມື້ອື່ນ")
    if not let_go_items:
        let_go_items.append("ສິ່ງທີ່ຢູ່ນອກເໜືອການຄວບຄຸມ ແລະ ເລື່ອງທີ່ຍັງບໍ່ທັນເກີດຂຶ້ນ")

    milestone_tag = f"📈 Brain Dump ຄັ້ງທີ: {total_count}/10"
    if total_count < 10:
        milestone_tag += f" (ອີກ {10 - total_count} ຄັ້ງ ເປີດບົດວິເຄາະໃຫຍ່ 10-Run Deep Diagnosis)"
    else:
        milestone_tag += f" (ຄົບຮອບ Milestone! ພ້ອມສັງເຄາະລາຍງານໃຫຍ່)"

    reply_msg = (
        f"🌿 [Cloud 24/7] Jo NOY ໄດ້ຮັບ Brain Dump ແລ້ວ ({date_display})\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{milestone_tag}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 1. ສະພາວະທີ່ສຳຜັດໄດ້ (Mindset Snapshot):\n"
    )
    for e in detected_emotions:
        reply_msg += f"• {e}\n"
        
    reply_msg += "\n🎯 2. ເລື່ອງທີ່ຢູ່ໃນມືອ້າຍຊ້າງ (Circle of Control):\n"
    for c in control_items:
        reply_msg += f"• {c}\n"
        
    reply_msg += "\n🍃 3. ເລື່ອງທີ່ຄວນປ່ອຍວາງຕອນນີ້ (Circle of Concern / Let Go):\n"
    for l in let_go_items:
        reply_msg += f"• {l}\n"
        
    reply_msg += (
        "\n🛡️ 4. ຂໍ້ຄວາມຈາກ Jo NOY:\n"
        "\"ອ້າຍຊ້າງເຮັດໄດ້ດີຫຼາຍແລ້ວ! ທຸກຄັ້ງທີ່ເຮົາເທມັນອອກມາ ຫົວເຮົາຈະໂລ່ງຂຶ້ນເລື້ອຍໆ.\n"
        "ສູ້ໄປນຳກັນເດີອ້າຍຊ້າງ... Jo NOY ແລະ ທີມ AI OS ຈະເປັນຫຼັງພິງທີ່ໜັກແໜ້ນໃຫ້ນາຍສະເໝີ!\"\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "☁️ ລະບົບ Cloud Server ເປີດເຮັດວຽກ 24/7 ແລ່ນຢູ່ເທິງ Render.com"
    )
    return reply_msg

def process_command(text):
    clean = text.strip()
    low = clean.lower()
    
    if low in ["/start", "/help", "help", "ຊ່ວຍເຫຼືອ"]:
        return (
            "🚀 ຍິນດີຕ້ອນຮັບສູ່ AI OS Remote Cockpit (Cloud 24/7 Edition)!\n\n"
            "ບັອດນີ້ເຮັດວຽກເທິງ Render.com ຕະຫຼອດ 24 ຊົ່ວໂມງ ແມ້ແຕ່ຕອນປິດຄອມ!\n\n"
            "• '🧠 Brain Dump (ເທຄວາມຄິດ)' -> ພິມເທຄວາມຄິດ, ຄວາມຄຽດ ຫຼື ເລື່ອງໃນຫົວ\n"
            "• '🎯 ຂໍສະຫຼຸບດ່ວນ' -> ດຶງ Action Cockpit ປະຈຳວັນ\n"
            "• '📊 ສະຖານະ OS' -> ເບິ່ງສະຖານະ Cloud Bot\n"
            "• '🧠 ກວດ SOP-04' -> ກວດຈຸດຄ້າງປິດຄວາມຈຳ\n"
        )
    elif low in ["/brief", "brief", "ສະຫຼຸບ", "🎯 ຂໍສະຫຼຸບດ່ວນ"]:
        return (
            "🎯 AI OS Action Cockpit (Cloud 24/7):\n\n"
            "• [⏱ 20m | ກ່ອນ 13:00] [Rivé Dining] ທັກ WhatsApp ຫາລູກຄ້າ ຢືນຢັນ QA Flag 2 ຈຸດ\n"
            "• [⏱ 15m | ກ່ອນ 15:00] [ALG] ກວດ & Approve ໂປສເຕີ 8K + ວິດີໂອ 4 ສາກ Batch 3\n"
            "• [⏱ 25m | ກ່ອນ 18:00] [M-chang] ໂພສຄລິບ 60s High-IQ Explainer ລົງ TikTok/Reels\n"
        )
    elif low in ["/status", "status", "ສະຖານະ", "📊 ສະຖານະ os"]:
        return (
            "📊 ສະຖານະ Cloud Remote Bot (Render.com):\n\n"
            "• ສະຖານະ: 🟢 ONLINE 24/7 (Always-on)\n"
            f"• ຈຳນວນ Brain Dump ສະສົມ: {len(DUMPS_STORE)}/10 ຄັ້ງ\n"
            f"• ເວລາເຊີບເວີ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
    elif low in ["/sop4", "sop4", "🧠 ກວດ sop-04"]:
        return (
            "🧠 SOP-04 Memory Audit:\n\n"
            "1. PROJECT-RIVE_CHRISTMAS_2026: ກຳລັງລໍຖ້າລູກຄ້າຕອບ QA Flag ເພື່ອປິດ V3\n"
            "2. PROJECT-04_ALG: Batch 3 ຍັງຄ້າງ 'ລໍອ້າຍຊ້າງກວດ'\n"
            "3. M-chang: ຄລິບ 60s Explainer ພ້ອມໂພສ\n\n"
            "👉 ເມື່ອເປີດຄອມແລ້ວເຮັດວຽກໃດໜຶ່ງສຳເລັດ ພຽງພິມ 'ໃຊ້ sop4' ໃນແຊັດ AI OS ຈະບັນທຶກຄວາມຈຳ 2 ຊັ້ນທັນທີ!"
        )
    elif low in ["🧠 brain dump (ເທຄວາມຄິດ)", "brain dump", "ເທຄວາມຄິດ"]:
        return (
            f"🧘‍♂️ [Cloud 24/7] ພ້ອມຮັບຟັງ 100% ແລ້ວອ້າຍຊ້າງ!\n\n"
            "ຕອນນີ້ພິມທຸກຢ່າງທີ່ຢູ່ໃນຫົວອອກມາໄດ້ເລີຍ: ບໍ່ຕ້ອງຢຸດຄິດ, ບໍ່ຕ້ອງສົນໃຈໄວຍາກອນ...\n\n"
            "👉 ພຽງພິມຂຶ້ນຕົ້ນດ້ວຍ 'ເທ ...' ຫຼື ພິມຂໍ້ຄວາມຍາວໆ ສົ່ງມາເລີຍ Jo NOY ຈະຊ່ວຍແຍກແຍະ ແລະ ວິເຄາະໃຫ້ຫົວໂລ່ງທັນທີ!"
        )
    elif low.startswith("ເທ ") or low.startswith("dump ") or low.startswith("/dump ") or low.startswith("/braindump "):
        parts = clean.split(" ", 1)
        raw_dump = parts[1] if len(parts) > 1 else ""
        if not raw_dump:
            return "⚠️ ກະລຸນາພິມຂໍ້ຄວາມຕໍ່ທ້າຍຄຳວ່າ 'ເທ' ເຊັ່ນ: `ເທ ຮູ້ສຶກຄຽດເລື່ອງ...`"
        return process_brain_dump(raw_dump)
    else:
        if len(clean) > 80:
            return process_brain_dump(clean)
        return (
            f"🤖 [Cloud 24/7] ໄດ້ຮັບຂໍ້ຄວາມ: \"{clean}\"\n\n"
            "💡 ຖ້າຢາກເທຄວາມຄິດ ພິມຂຶ້ນຕົ້ນດ້ວຍ 'ເທ ...' ຫຼື ພິມລະບາຍມາຍາວໆ ໄດ້ເລີຍເດີອ້າຍຊ້າງ!"
        )

# Webhook HTTP Request Handler for Render
class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "running", "service": "AI OS Cloud Cockpit"}).encode("utf-8"))
        
    def do_POST(self):
        if self.path == "/webhook" or self.path.startswith("/webhook"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode("utf-8"))
                msg = data.get("message")
                if msg:
                    chat_id = str(msg.get("chat", {}).get("id"))
                    text = msg.get("text")
                    # Security filter: only allow Aiy chang!
                    if chat_id == str(ALLOWED_CHAT_ID) and text:
                        reply = process_command(text)
                        send_telegram_message(chat_id, reply, get_keyboard())
            except Exception as e:
                print(f"[ERROR] Webhook error: {e}")
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    print(f"[INIT] Cloud Server listening on port {PORT}...")
    server.serve_forever()

# Setup Webhook with Telegram
def setup_webhook_if_needed():
    if RENDER_URL and TOKEN:
        webhook_url = f"{RENDER_URL.rstrip('/')}/webhook"
        print(f"[SETUP] Configuring Telegram Webhook to: {webhook_url}")
        target = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={urllib.parse.quote(webhook_url)}"
        try:
            with urllib.request.urlopen(target, timeout=10) as resp:
                print(f"[SETUP] Webhook response: {resp.read().decode()}")
        except Exception as e:
            print(f"[SETUP] Failed to set webhook: {e}")

if __name__ == "__main__":
    if not TOKEN or not ALLOWED_CHAT_ID:
        # Load from .env if running locally
        env_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_f):
            with open(env_f) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        if k == "TELEGRAM_BOT_TOKEN": TOKEN = v
                        if k == "TELEGRAM_CHAT_ID": ALLOWED_CHAT_ID = v

    setup_webhook_if_needed()
    run_server()
