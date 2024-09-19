import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "YOUR TELEGRAM TOKEN HERE"

DOWNLOAD_FOLDER = './'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Send me a YouTube link and I will convert it to MP3 for you.')

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id

    if update.message.text and ('youtube.com' in update.message.text or 'youtu.be' in update.message.text):
        try:
            youtube_url = update.message.text
            
            # Download the audio using yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                mp3_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            # Send the MP3 file to the user
            await context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file_path, 'rb'))

            # Clean up the MP3 file after sending
            os.remove(mp3_file_path)

        except Exception as e:
            logging.error(f"Error processing YouTube link: {e}")
            await update.message.reply_text("Error processing YouTube link. Please try again.")

    else:
        await update.message.reply_text("Please provide a valid YouTube link.")

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
