import telebot
import requests
import re
import time
import csv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import socket
from colorama import init, Fore
from dotenv import load_dotenv 
import telebot
import sys
import psutil
import os

# Anti-debugging and environment checks
def check_debugger():
    if sys.gettrace():  # Verifica si hay un depurador en ejecución
        print("Debugger detected! Exiting...")
        sys.exit(1)

def check_suspicious_processes():
    suspicious = ["strace", "gdb", "ltrace", "frida"]  # Lista de herramientas de depuración
    for proc in psutil.process_iter(["name"]):
        if any(s in proc.info["name"].lower() for s in suspicious):
            print("Suspicious process detected! Exiting...")
            sys.exit(1)

def check_logging():
    if not sys.stdout.isatty():  # Verifica si la salida estándar está redirigida
        print("¡No puedes descifrarme!")
        sys.exit(1)

# Ejecutar las comprobaciones al inicio del bot
check_debugger()
check_suspicious_processes()
check_logging()

import telebot
import requests
import re
import time
import csv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import socket
from colorama import init, Fore
from dotenv import load_dotenv 

# Inicializamos Colorama
init(autoreset=True)

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener el token desde las variables de entorno
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Verificar si el token se cargó correctamente
if not BOT_TOKEN:
    raise ValueError("The bot token is not configured. Verify the .env file.")
# Inicializar el bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")  # Activar soporte para Markdown

# URL de la API externa
API_URL = "https://domains.yougetsignal.com/domains.php"


# Archivo para registrar usuarios
LOG_FILE = "log.csv"
# Directorio donde se guardarán los historiales
HISTORY_DIR = "user_histories"
# Crear el directorio si no existe
os.makedirs(HISTORY_DIR, exist_ok=True)
# Idiomas soportados
# Directorio para guardar archivos temporales
TEMP_DIR = "temp_results"
os.makedirs(TEMP_DIR, exist_ok=True)
LANGUAGES = {
    "es": {
        "welcome": (
            "👋 *¡Bienvenido al bot de búsqueda DomainSpyBot!* 🚀\n\n"
            "Envíame una dirección IP o un dominio para buscar los dominios asociados.\n\n"
            "📚 *Comandos disponibles:*\n"
            "`/start` - Mostrar este mensaje de bienvenida.\n"
            "`/setlang [es|en]` - Cambiar el idioma del bot.\n"
            "`/history` - Mostrar tu historial de consultas.\n"
            "`/stats` - Ver estadísticas del bot.\n"
            "`/port [dominio]` - Escanear puertos abiertos de un dominio.\n"
            "`/ip [dominio]` - Obtener la dirección IP de un dominio.\n\n"
            "✨ *Ejemplo:* Escribe `8.8.8.8` o `google.com` para buscar los dominios relacionados.\n\n"
            "👨‍💻 *Desarrollado por:* *@Gh0stDeveloper*\n"
        ),
        "invalid_input": "❌ *Entrada inválida.* Por favor, envía una dirección IP (e.g., `8.8.8.8`) o un dominio (e.g., `example.com`).",
        "searching": "🔍 *Buscando dominios asociados a:* `{query}`\n\n_Esto puede tardar unos segundos. Por favor, espera..._",
        "no_results": "🔎 *No se encontraron dominios asociados.*",
        "results_header": "🌐 *Resultados para:* `{query}`\n_Se encontraron {count} dominios asociados:_\n",
        "completed": "✅ *Búsqueda completada en {time:.2f} segundos.*",
        "change_language": "✅ *Idioma cambiado a Español.*",
        "no_language": "❌ *Idioma no soportado.*",
        "stats": "📊 *Estadísticas del bot:*\nUsuarios únicos: {users}\nConsultas realizadas: {queries}",
    },
    "en": {
        "welcome": (
            "👋 *Welcome to the DomainSpyBot Lookup bot!* 🚀\n\n"
            "Send me an IP address or domain to search for associated domains.\n\n"
            "📚 *Available commands:*\n"
            "`/start` - Show this welcome message.\n"
            "`/setlang [es|en]` - Change the bot language.\n"
            "`/history` - Show your query history.\n"
            "`/stats` - View bot statistics.\n"
            "`/port [domain]` - Scan open ports of a domain.\n"
            "`/ip [domain]` - Get the IP address of a domain.\n\n"
            "✨ *Example:* Type `8.8.8.8` or `google.com` to look for related domains.\n\n"
            "👨‍💻 *Developed by:* *@Gh0stDeveloper*\n"
        ),
        "invalid_input": "❌ *Invalid input.* Please send an IP address (e.g., `8.8.8.8`) or a domain (e.g., `example.com`).",
        "searching": "🔍 *Searching for domains associated with:* `{query}`\n\n_This might take a few seconds. Please wait..._",
        "no_results": "🔎 *No associated domains found.*",
        "results_header": "🌐 *Results for:* `{query}`\n_Found {count} associated domains:_\n",
        "completed": "✅ *Search completed in {time:.2f} seconds.*",
        "change_language": "✅ *Language changed to English.*",
        "no_language": "❌ *Language not supported.*",
        "stats": "📊 *Bot Statistics:*\nUnique users: {users}\nQueries made: {queries}",
    }
}

# Variables globales
user_queries = {}
user_language = {}
user_results = {}  # Para almacenar resultados por usuario (paginación)
stats = {"unique_users": set(), "total_queries": 0}

# Guardar usuario en el archivo log.csv
def log_user(user_id, username):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, username or "NoUsername"])


# Obtener texto traducido
def get_translation(user_id, key):
    lang = user_language.get(user_id, "es")
    return LANGUAGES[lang].get(key, key)

# Validar IP o dominio
def is_valid_ip_or_domain(query):
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"  # Para direcciones IP válidas
    domain_pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]+)+$"  # Para dominios, incluyendo subdominios y extensiones largas
    return re.match(ip_pattern, query) or re.match(domain_pattern, query)

# Consulta Reverse IP Lookup
def reverse_ip_lookup(query):
    payload = {"remoteAddress": query}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.post(API_URL, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "Success":
            domains = data.get("domainArray", [])
            if not domains:
                return []
            
            # Formatear resultados
            results = [
                f"{i + 1}. {item[0]}" 
                for i, item in enumerate(domains)
            ]
            return results
        else:
            return []
    except Exception:
        return []

def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)

# Crear botones de paginación con opción de descargar resultados
def create_pagination_buttons(user_id, current_page, page_size=5):
    results = user_results[user_id]
    total_pages = (len(results) - 1) // page_size + 1
    markup = InlineKeyboardMarkup()

    # Botón para ir a la página anterior
    if current_page > 1:
        markup.add(InlineKeyboardButton("⬅️ Anterior", callback_data=f"page:{current_page - 1}"))
    
    # Botón para ir a la página siguiente
    if current_page < total_pages:
        markup.add(InlineKeyboardButton("➡️ Siguiente", callback_data=f"page:{current_page + 1}"))
    
    # Botón para descargar resultados como archivo
    markup.add(InlineKeyboardButton("📄 Descargar resultados", callback_data="download:results"))
    
    return markup


# Función para limpiar el nombre del dominio y hacerlo seguro para el sistema de archivos
def sanitize_filename(domain):
    # Reemplazar caracteres no válidos por guiones bajos o eliminarlos
    return re.sub(r'[^a-zA-Z0-9_-]', ' ', domain)

# Función para manejar la descarga de resultados
@bot.callback_query_handler(func=lambda call: call.data == "download:results")
def handle_download_results(call):
    user_id = call.message.chat.id
    results = user_results.get(user_id, [])

    if not results:
        bot.answer_callback_query(call.id, "❌ No hay resultados para descargar.")
        return

    # Obtener el dominio (asumimos que el primer resultado es el dominio o subdominio de interés)
    query = user_queries.get(user_id, [""])[0]
    domain = query.split("/")[0]  # Si el query tiene un subdominio, tomar solo la parte principal
    sanitized_domain = sanitize_filename(domain)

    # Crear un archivo de texto con el nombre del dominio
    filename = os.path.join(TEMP_DIR, f"resultados {sanitized_domain}.txt")
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(results))
    
    # Enviar el archivo al usuario
    with open(filename, "rb") as file:
        bot.send_document(chat_id=user_id, document=file, caption="📄 Aquí están tus resultados completos.")

    # Confirmar la acción al usuario
    bot.answer_callback_query(call.id, "✅ Archivo enviado.")

    # Opcional: Eliminar el archivo temporal después de enviarlo
    os.remove(filename)
    

# Guardar una consulta en el historial del usuario
def save_user_history(user_id, query):
    file_path = os.path.join(HISTORY_DIR, f"{user_id}.txt")
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"{query}\n")

# Leer el historial del usuario
def get_user_history(user_id):
    file_path = os.path.join(HISTORY_DIR, f"{user_id}.txt")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()
        
# Manejo de paginación
@bot.callback_query_handler(func=lambda call: call.data.startswith("page:"))
def handle_pagination(call):
    try:
        user_id = call.message.chat.id
        current_page = int(call.data.split(":")[1])
        page_size = 10  # Establecer el tamaño de la página a 10 resultados por página
        results = user_results[user_id]
        start = (current_page - 1) * page_size
        end = start + page_size
        page_results = results[start:end]

        new_text = "\n".join(page_results)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=new_text,
            parse_mode="Markdown",
            reply_markup=create_pagination_buttons(user_id, current_page, page_size)  # Pasar el current_page correcto
        )
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}")

# Comando /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.chat.id
    username = message.from_user.username
    log_user(user_id, username)
    stats["unique_users"].add(user_id)
    bot.reply_to(message, get_translation(user_id, "welcome"))

# Comando /setlang
@bot.message_handler(commands=["setlang"])
def set_language(message):
    user_id = message.chat.id
    lang = message.text.split(" ")[1] if len(message.text.split()) > 1 else ""
    if lang in LANGUAGES:
        user_language[user_id] = lang
        bot.reply_to(message, get_translation(user_id, "change_language"))
    else:
        bot.reply_to(message, get_translation(user_id, "no_language"))

# Comando /stats
@bot.message_handler(commands=["stats"])
def show_stats(message):
    user_id = message.chat.id
    stats_text = get_translation(user_id, "stats").format(
        users=len(stats["unique_users"]),
        queries=stats["total_queries"]
    )
    bot.reply_to(message, stats_text)


# Comando /history mejorado
@bot.message_handler(commands=["history"])
def show_history(message):
    user_id = message.chat.id
    history = get_user_history(user_id)
    
    if history:
        formatted_history = "\n".join([f"{i + 1}. {query.strip()}" for i, query in enumerate(history)])
        bot.reply_to(message, f"📂 *Tu historial de consultas:*\n\n{formatted_history}")
    else:
        bot.reply_to(message, "📂 *No tienes historial de consultas.*")

# Comando /port para analizar los puertos abiertos de un dominio o subdominio. 
@bot.message_handler(commands=['port'])
def handle_port_scan(message):
    domain = message.text.split()[1]  # Obtiene el dominio o subdominio después del comando

    try:
        # Notificar que el escaneo ha comenzado
        bot.send_message(message.chat.id, "🔍 Comenzando el escaneo de puertos... Espere un momento por favor ⏳", 
                         reply_to_message_id=message.message_id)

        # Ejecuta el script externo que hemos creado para analizar los puertos
        result = subprocess.run(['python', 'ports.py', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Verifica si hubo algún error al ejecutar el script externo
        if result.stderr:
            bot.send_message(message.chat.id, f"❌ Error al ejecutar el script: {result.stderr}", 
                             reply_to_message_id=message.message_id)
            return

        # Envía el resultado del script al usuario, respondiendo al mensaje original
        bot.send_message(message.chat.id, result.stdout, reply_to_message_id=message.message_id)

    except Exception as e:
        bot.send_message(message.chat.id, f"❗ Ocurrió un error inesperado: {e}", 
                         reply_to_message_id=message.message_id)


# Muestra las ips de los dominios 
@bot.message_handler(commands=['ip'])
def handle_ip_lookup(message):
    input_text = message.text.split()
    
    if len(input_text) < 2:
        bot.reply_to(message, "❌ Debes proporcionar un dominio después del comando. Ejemplo: /ip example.com")
        return
    
    domain = input_text[1]
    
    try:
        # Resuelve el dominio a una IP
        ip_address = socket.gethostbyname(domain)
        bot.reply_to(message, f"🌐 La dirección IP de {domain} es: {ip_address}")
    except socket.gaierror:
        bot.reply_to(message, f"❌ No se pudo resolver el dominio {domain}.")
    except Exception as e:
        bot.reply_to(message, f"❗ Ocurrió un error: {e}")

# Manejar consultas de usuarios
@bot.message_handler(func=lambda message: True)
def handle_query(message):
    user_id = message.chat.id
    query = message.text.strip()

    if not is_valid_ip_or_domain(query):
        bot.reply_to(message, get_translation(user_id, "invalid_input"))
        return

    # Guardar la consulta en el historial del usuario
    save_user_history(user_id, query)

    bot.reply_to(message, get_translation(user_id, "searching").format(query=query))

    start_time = time.time()
    results = reverse_ip_lookup(query)
    execution_time = time.time() - start_time

    stats["total_queries"] += 1
    user_queries.setdefault(user_id, []).append(query)

    if results:
        user_results[user_id] = results  # Guardar resultados para paginación
        page_size = 10  # Reducir la cantidad de resultados por página
        first_page = results[:page_size]

        bot.send_message(
            chat_id=message.chat.id,
            text=get_translation(user_id, "results_header").format(query=query, count=len(results)) + "\n".join(first_page),
            reply_markup=create_pagination_buttons(user_id, current_page=1, page_size=page_size),
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(message, get_translation(user_id, "no_results"))

    bot.send_message(
        chat_id=message.chat.id,
        text=get_translation(user_id, "completed").format(time=execution_time)
    )



# Función para limpiar la pantalla
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Mensaje de bienvenida
def print_welcome_message():
    clear_screen()  # Limpiar la pantalla antes de mostrar el mensaje
    time.sleep(1)   # Espera breve para el efecto visual

    # Mensaje con colores
    print(Fore.CYAN + "="*50)
    print(Fore.MAGENTA + "  🖥️ DomainSpyBot  🖥️")
    print(Fore.GREEN + "    🚀 Desarrollador: @Gh0stDeveloper")
    print(Fore.YELLOW + "    👾 GitHub: @CHICO-CP")
    print(Fore.RED + "    🌍 Puedes hablar conmigo en Telegram.")
    print(Fore.CYAN + "="*50)
    print(Fore.BLUE + "Bot activado y esperando comandos...")
    print(Fore.CYAN + "="*50)

# Iniciar el bot en modo de polling
print_welcome_message()

# Iniciar el bot
bot.infinity_polling()