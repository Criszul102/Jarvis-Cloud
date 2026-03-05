import os
import asyncio
import edge_tts
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. TRUCO PARA RENDER (Engañar al escaneo de puertos) ---
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
    texto_usuario = update.message.text
    
    # Jarvis piensa con Groq (CORREGIDO EL ERROR DE LISTA)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Jarvis, el asistente de Tony Stark. Hablas con un toque colombiano culto (patrón, elegancia)."},
            {"role": "user", "content": texto_usuario}
        ],
    )
    
    # EL CAMBIO ESTÁ AQUÍ: Añadimos [0] para elegir la primera respuesta de la lista
    respuesta_texto = completion.choices[0].message.content

    # Gonzalo genera el audio
    archivo_voz = f"voz_{update.message.chat_id}.mp3"
    await edge_tts.Communicate(f"... {respuesta_texto}", VOZ_COLOMBIA).save(archivo_voz)
    
    with open(archivo_voz, 'rb') as audio:
        await update.message.reply_voice(voice=audio, caption=respuesta_texto)
    
    if os.path.exists(archivo_voz):
        os.remove(archivo_voz)

if __name__ == '__main__':
    # Lanzamos el servidor de mentira para que Render esté feliz
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    print("Jarvis en línea y engañando a los puertos de Render...")
    application = Application.builder().token(TOKEN_TELEGRAM).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    application.run_polling()
