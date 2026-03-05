import os
import asyncio
import edge_tts
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VOZ_COLOMBIA = "es-CO-GonzaloNeural"

client = Groq(api_key=GROQ_API_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text
    print(f"El patrón dijo: {texto_usuario}")

    # 1. Jarvis piensa con Groq
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Jarvis, el asistente de Tony Stark. Hablas con un toque colombiano culto (patrón, elegancia)."},
            {"role": "user", "content": texto_usuario}
        ],
    )
    respuesta_texto = completion.choices.message.content

    # 2. Gonzalo genera el audio (Sin Pygame)
    archivo_voz = f"voz_{update.message.chat_id}.mp3"
    communicate = edge_tts.Communicate(f"... {respuesta_texto}", VOZ_COLOMBIA)
    await communicate.save(archivo_voz)
    
    # 3. Enviamos el audio directo a tu Telegram
    with open(archivo_voz, 'rb') as audio:
        await update.message.reply_voice(voice=audio, caption=respuesta_texto)
    
    # 4. Limpieza de archivos en la nube
    if os.path.exists(archivo_voz):
        os.remove(archivo_voz)

if __name__ == '__main__':
    print("Jarvis en línea. Esperando órdenes en Telegram, patrón...")
    application = Application.builder().token(TOKEN_TELEGRAM).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    application.run_polling()
