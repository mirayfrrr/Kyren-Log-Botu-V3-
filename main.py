import os, telebot, json, traceback, time, random, re
from telebot import types

tok = '8112395786:AAHuXd9og3hmgUId5BO46QnckvLQd5kSc-Q'
bot = telebot.TeleBot(tok)

ADMİN = ["7864975785"]


# Deaktörler Liste
DEAKTÖRLER = ["@error_handler", "@ban", "@id"]

def decorators(func):
    decorators = []
    for decorator in DEAKTÖRLER:
        if decorator == "@error_handler":
            decorators.append(error_handler)
        elif decorator == "@ban":
            decorators.append(ban)
        elif decorator == "@id":
            decorators.append(id)
    for decorator in reversed(decorators):
        func = decorator(func)
    return func
    
    

def kurucu(func):
    def wrapper(message):
        user_id = str(message.from_user.id)
        if user_id not in ADMİN:  
            bot.reply_to(message, "❌ Sadece Kurucu Bu Komutu Kullanabilir.")
            return
        return func(message)
    return wrapper
    
#----------------- ID Kaydetme Sistemi -----------------#

ID_FILE = "id.txt"

def load_ids():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  
    return []

def save_ids(user_ids):
    with open(ID_FILE, "w") as f:
        json.dump(user_ids, f, indent=4)

def id(func):
    def wrapper(message):
        user_id = str(message.from_user.id)
        users = load_ids()

        if user_id not in users:
            users.append(user_id)
            save_ids(users)
        return func(message)
    return wrapper

    
#----------------- ID Kaydetme Sistemi -----------------#
    
    
    
    
#----------------- Hata Kontrol Sistemi -----------------#

MAX_LOG_SIZE = 1 * 1024 * 1024

def log_error_to_file(error_trace):
    log_file = "Hata.txt"
    if os.path.exists(log_file) and os.path.getsize(log_file) >= MAX_LOG_SIZE:
        with open(log_file, "w") as error_file:
            error_file.write("✅ Eski Loglar Temizlendi. Yeni Loglar :\n\n")

    with open(log_file, "a") as error_file:
        error_file.write(error_trace + "\n\n")

def save_long_error_to_txt(error_trace):
    txt_file = "Hata_Mesajı.txt"
    with open(txt_file, "w") as file:
        file.write(error_trace)
    return txt_file

def send_error_to_ADMİN(error_trace, bot):
    if len(error_trace) > 4096:
        txt_file = save_long_error_to_txt(error_trace)
        for user_id in ADMİN:
            try:
                with open(txt_file, "rb") as file:
                    bot.send_document(user_id, file, caption="🚨 Hata Mesajı ( Metin Çok Uzun Olduğu İçin Dosya Olarak Gönderildi ) !")
            except Exception as e:
                print(f"Hata Dosyası Gönderilemedi : {e}")
        os.remove(txt_file)
    else:
        short_error = error_trace.splitlines()[-1]
        for user_id in ADMİN:
            try:
                bot.send_message(user_id, f"🚨 Yeni Bir Hata Tespit Edildi :\n\n{short_error}", parse_mode='Markdown')
            except Exception as e:
                print(f"Hata Mesajı Gönderilemedi : {e}")

def error_handler(func):
    def wrapper(message):
        try:
            return func(message)
        except Exception as e:
            error_message = "❌ *Error :* Bir Sorun Oluştu, Sorun Admin'lere Bildirildi."
            bot.reply_to(message, error_message, parse_mode='Markdown')

            error_trace = traceback.format_exc()
            log_error_to_file(error_trace)
            send_error_to_ADMİN(error_trace, bot)

            bot.send_message(message.chat.id, "📝 *Not :* Hata Ve Verdiğimiz Rahatsızlık İçin Özür Dileriz. Başka Bir Komut Kullanabilirsiniz.", parse_mode='Markdown')
    return wrapper

if not os.path.exists("Hata.txt"):
    with open("Hata.txt", "w") as f:
        pass


#----------------- Hata Kontrol Sistemi -----------------#



#----------------- Admin Sistemi -----------------#


def admin(func):
    def wrapper(message):
        user_id = str(message.from_user.id)
        admin_users = load_admins()

        if user_id not in ADMİN and user_id not in admin_users:
            bot.reply_to(message, "❌ Yetkili Kullanıcı Değilsiniz!\nBu Komutu Kullanamazsınız.")
            return
        return func(message)
    return wrapper

ADMIN_FILE = 'Admin.txt'

def load_admins():
    if not os.path.exists(ADMIN_FILE):  
        with open(ADMIN_FILE, 'w') as f:  
            json.dump([], f)
    with open(ADMIN_FILE, 'r') as f:
        return json.load(f)

def save_admins(admin_list):
    with open(ADMIN_FILE, 'w') as f:
        json.dump(admin_list, f)

@bot.message_handler(commands=['admin'])
@error_handler
@kurucu
def grant_admin(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].isdigit():
            bot.reply_to(message, "❌ Lütfen Geçerli ID Girin.\nKullanım: /admin <ID>")
            return

        user_to_admin = parts[1]
        admin_users = load_admins()
        if user_to_admin not in admin_users:
            admin_users.append(user_to_admin)
            save_admins(admin_users)  
            bot.reply_to(message, f"✅ Kullanıcı {user_to_admin} Admin Olarak Eklendi!")
        else:
            bot.reply_to(message, f"❌ Kullanıcı {user_to_admin} Zaten Admin.")
    except IndexError:
        bot.reply_to(message, "❌ Yanlış Kullanım. Lütfen ID'yi Girin.\nÖrnek Kullanım: /admin <id>")

@bot.message_handler(commands=['unadmin'])
@error_handler
@kurucu  
def remove_admin(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].isdigit():
            bot.reply_to(message, "❌ Lütfen Geçerli ID Girin.\nKullanım: /unadmin <ID>")
            return

        user_to_remove = parts[1]
        admin_users = load_admins()
        if user_to_remove in admin_users:
            admin_users.remove(user_to_remove)
            save_admins(admin_users)  
            bot.reply_to(message, f"✅ Kullanıcı {user_to_remove} Adminlikten Çıkarıldı!")
        else:
            bot.reply_to(message, f"❌ Kullanıcı {user_to_remove} Admin Listesinde Değil.")
    except IndexError:
        bot.reply_to(message, "❌ Yanlış Kullanım. Lütfen ID'yi Girin.\nÖrnek Kullanım: /unadmin <id>")

#----------------- Admin Sistemi -----------------#


#----------------- Ban Sistemi -----------------#

def ban(func):
    def wrapper(message):
        user_id = str(message.from_user.id)

        user_data = next((user for user in banned_users if user["id"] == user_id), None)
        if user_data:
            reason = user_data["reason"]
            bot.reply_to(
                message,
                f"🚫 *Kurallara Uymadığın için Hesabın Engellendi* !\n\n📨 *Sebep :* {reason}", parse_mode='Markdown'
            )
            return  
        return func(message)  
    return wrapper

BAN_FILE = 'Ban.json'

def load_banned_users():
    if os.path.exists(BAN_FILE):
        try:
            with open(BAN_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("❌ Hata: Ban.json dosyası bozuk. Liste sıfırlandı.")
            return []
    return []

def save_banned_users(banned_users):
    with open(BAN_FILE, 'w') as f:
        json.dump(banned_users, f, indent=4)  

banned_users = load_banned_users()

@bot.message_handler(commands=['ban'])
@error_handler
@admin
def eban_command(message):
    try:
        args = message.text.split(maxsplit=2)
        user_id = args[1]  
        reason = args[2] if len(args) > 2 else "Belirtilmemiş" 
        
        if not any(user["id"] == user_id for user in banned_users):
            banned_users.append({"id": user_id, "reason": reason})  
            save_banned_users(banned_users)
            bot.send_message(
                user_id,
                f"🚫 *Kurallara Uymadığın için Hesabın Engellendi* !\n\n📨 *Sebep :* {reason}", parse_mode='Markdown'
            )
            bot.reply_to(message, f"✅ {user_id} Başarıyla Engellendi.")
        else:
            bot.reply_to(message, f"❌ {user_id} Zaten Engellenmiş.")
    except IndexError:
        bot.reply_to(message, "❌ Yanlış Kullanım !\nÖrnek : /ban <user_id> <sebep>")



@bot.message_handler(commands=['unban'])
@admin  
def elleneste_unban(message):
    try:
        user_to_unban = message.text.split(maxsplit=1)[1]

        user_data = next((user for user in banned_users if user["id"] == user_to_unban), None)
        if user_data:
            banned_users.remove(user_data)
            save_banned_users(banned_users)
            bot.reply_to(message, f"✅ {user_to_unban} ID'li Kullanıcının Banı Kaldırıldı.")
        else:
            bot.reply_to(message, f"❌ {user_to_unban} Bu Listede Banlı Değil.")
    except IndexError:
        bot.reply_to(message, "❌ Yanlış Kullanım.\nÖrnek Kullanım: /unban <kullanıcı_id>")
        
#----------------- Ban Sistemi -----------------#



#----------------- Duyuru Gönderme Sistemi -----------------#

announcement_in_progress = {}

@bot.message_handler(commands=['duyuru'])
@error_handler
@admin
def duyuru(message):
    users = load_ids()  

    if not users:
        bot.reply_to(message, "⚠️ Duyuru Gönderilecek Kayıtlı Kullanıcı Bulunamadı.")
        return

    try:
        announcement_text = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "❌ Lütfen Duyuru Mesajını Yazın.\nÖrnek kullanım: /duyuru <mesaj>")
        return

    announcement_in_progress[message.from_user.id] = announcement_text

    msg = bot.reply_to(message, "💗 Duyuruyu Fotoğraf Veya Video İle Mi Göndermek İstiyorsunuz ?\n\nDosyayı Ekleyin Veya 'Hayır' Yazın.")
    bot.register_next_step_handler(msg, lambda response: handle_media_or_text(response, users))


def handle_media_or_text(response, users):
    user_id = response.from_user.id
    announcement_text = announcement_in_progress.get(user_id)

    if not announcement_text:
        bot.reply_to(response, "❌ Bu komut yalnızca '/duyuru' ile başlatılabilir.")
        return

    if response.content_type == 'photo':
        photo_id = response.photo[-1].file_id
        bot.reply_to(response, f"📸 Fotoğraf Alındı! Duyuru Gönderimi Başlatılıyor...\n(Toplam {len(users)} kullanıcı)")

        for user in users:
            try:
                bot.send_photo(user, photo_id, caption=f"🔊 *ADMİNDEN DUYURU*\n\n{announcement_text}", parse_mode="Markdown")
                time.sleep(1)
            except Exception:
                pass

        bot.reply_to(response, "✅ *Fotoğraflı Duyuru Gönderimi Tamamlandı!*", parse_mode="Markdown")
    
    elif response.content_type == 'video':
        video_id = response.video.file_id
        bot.reply_to(response, f"🎥 Video Alındı! Duyuru Gönderimi Başlatılıyor...\n(Toplam {len(users)} kullanıcı)")

        for user in users:
            try:
                bot.send_video(user, video_id, caption=f"🔊 *ADMİNDEN DUYURU*\n\n{announcement_text}", parse_mode="Markdown")
                time.sleep(1)
            except Exception:
                pass

        bot.reply_to(response, "✅ *Videolu Duyuru Gönderimi Tamamlandı!*", parse_mode="Markdown")

    elif response.content_type == 'text' and response.text.lower() == 'hayır':
        bot.reply_to(response, f"Duyuru Gönderimi Başlatılıyor...\n(Toplam {len(users)} kullanıcı)")
        
        for user in users:
            try:
                bot.send_message(user, f"🔊 *ADMİNDEN DUYURU*\n\n{announcement_text}", parse_mode="Markdown", disable_web_page_preview=True)
                time.sleep(1)
            except Exception:
                pass

        bot.reply_to(response, "✅ *Mesajlı Duyuru Gönderimi Tamamlandı!*", parse_mode="Markdown")

    else:
        bot.reply_to(response, "❌ Geçersiz Yanıt! Fotoğraf, video ekleyin veya 'Hayır' yazın.")

    announcement_in_progress.pop(user_id, None)

#----------------- Duyuru Gönderme Sistemi -----------------#


@bot.message_handler(commands=['panel'])
@admin
def elleneste(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    diger_btn = types.InlineKeyboardButton("- - 𝐕 𝐈̇ 𝐏 - -", callback_data="diger")
    markup.add(diger_btn)
    
    bot.send_message(
        message.chat.id,
        "👋 Hoşgeldin, Admin 👨‍💻\n\n🫴 İşte Komutlar : ",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "diger")
@admin
def diger_komutlar(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    admin_ekle_sil_btn = types.InlineKeyboardButton("👨‍💻 Admin Ekle-Sil", callback_data="admin_ekle_sil")
    ban_at_kaldir_btn = types.InlineKeyboardButton("🪐 Ban At-Kaldır", callback_data="ban_at_kaldir")
    duyuru_yap_btn = types.InlineKeyboardButton("📢 Duyuru Yap", callback_data="duyuru_yap")
    oxy_btn = types.InlineKeyboardButton("📲 İletişim Cavapla", callback_data="oxy")
    
    markup.add(admin_ekle_sil_btn, ban_at_kaldir_btn, duyuru_yap_btn, oxy_btn)
    
    bot.send_message(
        call.message.chat.id,
        "👨‍💻 İşte Diğer Admin Komutları : ",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "admin_ekle_sil")
@kurucu
def admin_ekle_sil_komutlari(call):
    admin_komutlari = (
        "👨‍💻 Admin Ekle-Sil\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🥷 Admin Eklemek İçin\n"
        "/admin <ID> Şeklinde\n\n"
        "🥷 Admin Silmek İçin\n"
        "/admin_sil <ID> Şeklinde\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(call.message.chat.id, admin_komutlari)


@bot.callback_query_handler(func=lambda call: call.data == "ban_at_kaldir")
@admin
def ban_at_kaldir_komutlari(call):
    ban_komutlari = (
        "🪐 Ban At-Kaldır\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 Ban Atmak İçin\n"
        "/ban <ID> <sebep> Şeklinde\n\n"
        "🔓Ban Kaldırmak İçin\n"
        "/unban <ID> Şeklinde\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(call.message.chat.id, ban_komutlari)


@bot.callback_query_handler(func=lambda call: call.data == "duyuru_yap")
@admin
def duyuru_yap_komutlari(call):
    duyuru_komutlari = (
        "📢 Duyuru Yap\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔊 Duyuru Yapmak İçin\n"
        "/duyuru <mesaj> Şeklinde\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(call.message.chat.id, duyuru_komutlari)
    
    
@bot.callback_query_handler(func=lambda call: call.data == "oxy")
def oxy_komutlari(call):
    oxy_komutlari = (
        '''📱 Cevapla
 ━━━━━━━━━━━━━━━━━━━━━
 
 📲 /cevap - İletişimi Cevaplar     
/cevap <ID> <Mesaj>       
        
━━━━━━━━━━━━━━━━━━━━━'''
    )
    bot.send_message(call.message.chat.id, oxy_komutlari)
       





@bot.message_handler(commands=['start'])
@decorators
def start(message):
    isim = message.from_user.first_name
    user_id = message.from_user.id

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="📜 𝐊𝐨𝐦𝐮𝐭𝐥𝐚𝐫", callback_data="komutlar"))
    markup.add(types.InlineKeyboardButton(text="🗣️ 𝐇𝐚𝐤𝐤ı𝐦ı𝐳𝐝𝐚", callback_data="hakkimizda"))
    markup.add(types.InlineKeyboardButton(text="📞 𝐈̇𝐥𝐞𝐭𝐢𝐬̧𝐢𝐦", callback_data="iletisim"))

    bot.reply_to(message, f'''*Merhaba* 👋, [{isim}](tg://user?id={user_id})

🔮 Ben Çok Kapsamlı Bir Log Botuyum. Beni Kullanarak Log Çekebilir, Log'lardaki URL'leri Temizleyebilir Ve Birçok Şey Yapabilirsin.

Bir Sıkıntı Veya Önerin Olursa İletişim Kısmına Mesajını Bırak. ☎️''', parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "komutlar")
def komutlar_callback(call):
    bot.send_message(call.message.chat.id, '''📜 𝐈‌𝐬‌𝐭𝐞 𝐊𝐨𝐦𝐮𝐭𝐥𝐚𝐫 :

🔹 /log – Bir Site’den Log Çekmenizi Sağlar.

🔸 /urltemizle – (url:email:pass) Formatını (email:pass) Haline Getiririm.

🔹 /proxy – Https ve Socks4 Proxy’leri Çekerim.

🔸 /qr – Bir Linki Qr Koduna Dönüştürmeye Yarar.''')

  parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "iletisim")
def iletisim_callback(call):
    msg = bot.send_message(call.message.chat.id, "📩 *Admine Göndermek İstediğiniz Mesajı Giriniz* :", parse_mode='Markdown')
    bot.register_next_step_handler(msg, handle_iletisim_message)

def handle_iletisim_message(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "Yok"
    iletisim_mesaj = message.text
    
    for admin_id in ADMİN:
        bot.send_message(admin_id, f"📞 *İletişim Mesajınız* !\n\n"
                                   f"*Kullanıcı Adı* : {user_name} (@{username})\n"
                                   f"*Kullanıcı ID* : `{user_id}`\n\n"
                                   f"💌 *Mesaj* : `{iletisim_mesaj}`", parse_mode='Markdown')
    
    bot.send_message(message.chat.id, "💌 *Admine Mesajınız İletildi* !\n"
                                      "Mesajınız İçin Teşekkürler 🙏", parse_mode='Markdown')



#log komut
LOGS_FOLDER = "logs"  

if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

@bot.message_handler(commands=['log'])
@ban
@id
def log(message):
    try:
        start_time = time.time()

        command_parts = message.text.split(" ", 1)
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ *Lütfen Site İsmi Girin* ! \n*Örnek Kullanım* : `/log exxen.com`", parse_mode='Markdown')
            return

        site_name = command_parts[1].strip()
        matching_lines = []

        for file_name in os.listdir(LOGS_FOLDER):
            if file_name.endswith(".txt"):
                file_path = os.path.join(LOGS_FOLDER, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        if site_name in line:
                            matching_lines.append(line.strip())

        if not matching_lines:
            bot.reply_to(message, f"❌ *Log Bulunulamadı, Daha Sonra Tekrar Deneyin*", parse_mode='Markdown')
            return

        random.shuffle(matching_lines)

        output_file_name = f"{site_name}.txt"
        with open(output_file_name, "w", encoding="utf-8") as output_file:
            output_file.write("\n".join(matching_lines))

        end_time = time.time()
        duration = round(end_time - start_time, 2)

        with open(output_file_name, "rb") as output_file:
            sent_message = bot.send_document(
                message.chat.id, 
                output_file,
                caption=(
                    f"✅ *Log Başarıyla Çekildi !*\n\n"
                    f"🔗 *Site* : [{site_name}]\n"
                    f"⏳ *Süre* : [{duration} Sn]\n"
                    f"📚 *Log Sayısı* : `{len(matching_lines)}`"
                ),
                parse_mode='Markdown'
            )

        os.remove(output_file_name)

    except Exception as e:
        bot.reply_to(message, f"⚠️ *Hata* : {str(e)}", parse_mode='Markdown')



#url temizle komut
@bot.message_handler(commands=['urltemizle'])
@decorators
def urltemizle(message):
    bot.send_message(message.chat.id, "*Url'leri Temizlenecek* (url:email:password) *Formatındaki Dosyayı Gönderin* !", parse_mode='Markdown')
    bot.register_next_step_handler(message, handle_file)

def handle_file(message):
    if message.document:
        if not message.document.file_name.endswith('.txt'):
            bot.send_message(message.chat.id, "❌ Bu Dosya Bir .Txt Dosyası Değil. Lütfen Geçerli Bir .Txt Dosyası Gönderin.")
            return
        
        try:
            file_id = message.document.file_id
            file = bot.get_file(file_id)
            downloaded_file = bot.download_file(file.file_path)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Dosya İndirilemedi. Hata: {e}")
            return
        
        try:
            with open("temp.txt", "wb") as f:
                f.write(downloaded_file)

            lines = []
            with open("temp.txt", "r", encoding="utf-8") as file:
                     for line in file:
                    cleaned_line = re.sub(r'\S+://\S+', '', line).strip()
                    
                    parts = cleaned_line.split(":")
                    if len(parts) >= 2:
                        email = parts[-2].strip()
                        password = parts[-1].strip()
                        
                        if email.endswith('@gmail.com'):
                            lines.append(f"{email}:{password}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Hata : {e}")
            return
        
        if not lines:
            bot.send_message(message.chat.id, "❌ Dosyada Geçerli `Email:Pass` Bilgisi Bulunamadı.")
            return
        
        try:
            original_file_name = message.document.file_name
            new_file_name = original_file_name.replace(".txt", "_✅.txt")
            
            with open(new_file_name, "w", encoding="utf-8") as file:
                file.write("\n".join(lines) + "\n")
            
            with open(new_file_name, "rb") as file:
                bot.send_document(message.chat.id, file, caption="*Url'ler Temizlendi.* ✅", parse_mode="Markdown")
            
            os.remove(new_file_name)
            os.remove("temp.txt")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Beklenmeyen Bir Hata Oluştu. Hata: {e}")
    else:
        bot.send_message(message.chat.id, "❌ Lütfen Bir Dosya Gönderin.")
        
        
        
#proxy komut
proxy_list = []

@bot.message_handler(commands=['proxy'])
@decorators
def send_proxy(message):
    global proxy_list

    try:
        if not proxy_list:
            response = requests.get(
                "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text", 
                verify=False
            )

            if response.status_code == 200:
                proxies = response.text.splitlines()
                for proxy in proxies:
                    if "SOCKS" in proxy:
                        proxy_type = "SOCKS4"
                    else:
                        proxy_type = "HTTP"

                    proxy_list.append((proxy, proxy_type))
            else:
                bot.reply_to(message, f"⛔ Proxy Çekilemedi : HTTP {response.status_code}")
                return

        if proxy_list:
            proxy, proxy_type = random.choice(proxy_list)
            bot.reply_to(message, f"✅ *Proxy* : {proxy}\n*Proxy Türü* : `{proxy_type}`", parse_mode='Markdown')
            proxy_list.remove((proxy, proxy_type))  
        else:
            bot.reply_to(message, "⛔ Tüm Proxyler Gönderildi.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Hata : {e}")
        


#qr code komut
def generate_qr(message):
    try:
        text = message.text.split(' ', 1)[1]        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        temp_file = f"temp_{message.chat.id}.png"
        img.save(temp_file)

        with open(temp_file, 'rb') as qr_file:
            bot.send_photo(message.chat.id, qr_file)

        os.remove(temp_file)
    except IndexError:
        bot.send_message(message.chat.id, '❌ Lütfen Bir Link Giriniz !\nÖrnek : /qr Google.com')


@bot.message_handler(commands=['qr'])
@decorators
def handle_qr_command(message):
    generate_qr(message)
        
def pinterest_resim_ara(keyword, num_images):
    url = f'https://api.pinterest.com/v3/search/pins/?rs=rs&asterix=true&query={keyword}&link_header=6&etslf=13831&video_autoplay_disabled=0&dynamic_grid_stories=6'
    
    headers = {
        'Host': 'api.pinterest.com',
        'accept-language': 'ar-IQ-u-nu-latn',
        'user-agent': 'Pinterest for Android/12.1.1 (ANY-LX2; 13)',
        'x-pinterest-app-type-detailed': '3',
        'x-pinterest-device': 'ANY-LX2',
        'x-pinterest-device-hardwareid': 'f13c94806c6f87d8',
        'x-pinterest-installid': '358e34e753134017be281d2c4cab571',
        'x-pinterest-appstate': 'active',
        'authorization': 'Bearer YOUR_ACCESS_TOKEN',
        'accept-encoding': 'gzip',
        'cookie': '_b=YOUR_COOKIE; _pinterest_ct=YOUR_COOKIE; _ir=0',
    }
    
    try:
        response = requests.get(url, headers=headers)
        pinterest = response.json()
        all_foto_urls = [pinterest['data'][i]['images']['200x']['url'] for i in range(len(pinterest['data']))]

        if len(all_foto_urls) < num_images:
            return all_foto_urls  
        else:
            selected_foto_urls = random.sample(all_foto_urls, num_images)
            return selected_foto_urls
    except Exception as e:
        print(f'Bir hata oluştu: {e}')
        return None





@bot.message_handler(commands=['cevap'])
@admin
def iletisim_cvp(message):
    if len(message.text.split()) < 3:
        bot.reply_to(message, "❌ Kullanım: /cevap <id> <mesaj>")
        return

    command_args = message.text.split(maxsplit=2)
    user_id = command_args[1]
    reply_message = command_args[2]

    try:
        bot.send_message(user_id, "📟")
        
        time.sleep(3)

        admin_name = message.from_user.first_name
        admin_username = message.from_user.username
        admin_id = message.from_user.id
        admin_message = (
            f"📮 *Admin'den Bir Mesajınız Var* !\n\n"
            f"*Admin İsmi* : {admin_name} (@{admin_username})\n"
            f"*Admin ID* : `{admin_id}`\n\n"
            f"💌 *Mesaj* : `{reply_message}`"
        )
        bot.send_message(user_id, admin_message, parse_mode='Markdown')
        bot.reply_to(message, " ✅ Mesaj Başarıyla Gönderildi. ")
    except Exception as e:
        bot.reply_to(message, f" ❌ Mesaj Gönderilemedi. Hata: {str(e)}")
        
        


print("Log Bot Aktif")
bot.polling(none_stop=True)

# -------------------- KEEP ALIVE KISMI -------------------- #
app = Flask("")

@app.route('/')
def home():
    return "Bot aktif!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# keep alive başlat
keep_alive()
