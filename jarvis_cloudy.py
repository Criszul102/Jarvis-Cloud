import os
import asyncio
import edge_tts
from groq import Groq
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- LLAVES ---
TOKEN_TELEGRAM = "TOKEN_TELEGRAM"
GROQ_API_KEY = "GROQ_API_KEY"
VOZ_COLOMBIA = "es-CO-GonzaloNeural"

client = Groq(api_key=GROQ_API_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ¿Es voz o texto?
    if update.message.voice:
        print("Recibiendo audio del patrón...")
        # 1. Descargamos el audio de Telegram
        archivo_ogg = await update.message.voice.get_file()
        await archivo_ogg.download_to_drive("audio.ogg")
        
        # 2. Groq traduce tu voz a texto (Whisper)
        with open("audio.ogg", "rb") as file:
            transcripcion = client.audio.transcriptions.create(
                file=("audio.ogg", file.read()),
                model="whisper-large-v3",
                language="es"
            )
        texto_usuario = transcripcion.text
        os.remove("audio.ogg")
    else:
        texto_usuario = update.message.text

    print(f"Patrón dijo: {texto_usuario}")

        # 3. Jarvis piensa (IA) - VERSIÓN CORREGIDA
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Jarvis, el asistente de Tony Stark. Hablas con un toque colombiano culto (patrón, elegancia)."},
            {"role": "user", "content": texto_usuario}
        ],
    )
    # EL CAMBIO ESTÁ AQUÍ: Añadimos [0] antes de .message
    respuesta_texto = completion.choices[0].message.content


    # 4. Gonzalo habla (Voz)
    archivo_voz = "respuesta.mp3"
    await edge_tts.Communicate(f"... {respuesta_texto}", VOZ_COLOMBIA).save(archivo_voz)
    
    with open(archivo_voz, 'rb') as audio:
        await update.message.reply_voice(voice=audio, caption=respuesta_texto)
    
    os.remove(archivo_voz)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, responder))
    app.run_polling()
