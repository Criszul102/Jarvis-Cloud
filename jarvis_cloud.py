import os
import asyncio
import edge_tts
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. TRUCO PARA RENDER ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), BaseHTTPRequestHandler)
    server.serve_forever()

# --- 2. CONFIGURACIÓN ---
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VOZ_COLOMBIA = "es-CO-GonzaloNeural"
client = Groq(api_key=GROQ_API_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ¿Es voz o texto?
    if update.message.voice:
        print("Recibiendo audio del patrón...")
        # 1. Descargamos el audio de Telegram
        archivo_ogg = await update.message.voice.get_file()
        ruta_ogg = "audio.ogg"
        await archivo_ogg.download_to_drive(ruta_ogg)
        
        # 2. Groq traduce tu voz a texto (Whisper)
        with open(ruta_ogg, "rb") as file:
            transcripcion = client.audio.transcriptions.create(
                file=(ruta_ogg, file.read()),
                model="whisper-large-v3",
                language="es"
            )
        texto_usuario = transcripcion.text
        os.remove(ruta_ogg)
    else:
        texto_usuario = update.message.text

    print(f"Patrón dijo: {texto_usuario}")

    # 3. Jarvis piensa (IA)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Jarvis, el asistente de Tony Stark. Hablas con un toque colombiano culto (patrón, elegancia)."},
            {"role": "user", "content": texto_usuario}
        ],
    )
    respuesta_texto = completion.choices[0].message.content

    # 4. Gonzalo genera el audio (Voz)
    archivo_voz = f"voz_{update.message.chat_id}.mp3"
    await edge_tts.Communicate(f"... {respuesta_texto}", VOZ_COLOMBIA).save(archivo_voz)
    
    with open(archivo_voz, 'rb') as audio:
        await update.message.reply_voice(voice=audio, caption=respuesta_texto)
    
    os.remove(archivo_voz)

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    print("Jarvis en línea y escuchando audios, patrón...")
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    # Ahora aceptamos TEXTO y VOZ
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, responder))
    app.run_polling()

from wakeonlan import send_magic_packet # Asegúrate de tener 'wakeonlan' en tu requirements.txt

# --- DATOS DE TU BASE STARK ---
MAC_TORRE = 'a0:ad:9f:b7:34:be' 
IP_CASA = 'TU_IP_PUBLICA_AQUI' # La que acabas de buscar en Google

def encender_torre():
    # Enviamos el paquete mágico desde la nube hasta tu router
    send_magic_packet(MAC_TORRE, ip_address=IP_CASA, port=9)
    return "Iniciando protocolo de arranque, patrón. La cincuenta sesenta Ti está despertando."

# Dentro de tu función 'responder', añade este comando:
if "enciende la torre" in texto_usuario:
    respuesta_texto = encender_torre()
