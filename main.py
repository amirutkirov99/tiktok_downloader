import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram import F
from aiogram.enums import ParseMode
import asyncio
import requests
import os
import re
from background import keep_alive

keep_alive()


def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


def download_tt(url_tiktok):
    url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"url\"\r\n\r\n{url_tiktok}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"hd\"\r\n\r\n1\r\n-----011000010111000001101001--\r\n\r\n"
    headers = {
        "x-rapidapi-key": "45f4e95f74mshb7231980c6f3821p13ff84jsnac7950a93cb8",
        "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
        "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
    }

    response = requests.post(url, data=payload, headers=headers)
    response_json = response.json()
    return response_json

# title = response_json['data']['title']
# hdplay = response_json['data']['play']
# print("Title:", title)
# print("HD Play URL:", hdplay)


# Введите сюда токен вашего бота
BOT_TOKEN = '6846762920:AAFYPWrc16abK9CK-oHknshcn22tiZAqkpE'
# Идентификатор чата
# CHAT_ID = '5527705092'
# URL видео
# video_url = "tiktok_videos/video.mp4"
video_url = "D:\Desktop\cru\\tiktok_videos\\video.mp4"


logging.basicConfig(level=logging.INFO)


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def download(url: str, path: str):
    # print("Загрузка")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(path, 'wb') as f:
                    f.write(await response.read())
                    # print("Скачалось")
            else:
                raise Exception(
                    f"Failed to download video, status code: {response.status}")


def delete_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
        else:
            pass
    except Exception as e:
        print(f"Не удалось удалить файл {path}: {e}")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(f"Добро пожаловать!\n\nВы можете скинуть мне ссылку на пост TikTok откуда нужно выгрузить видео и текст — через пару секунд этот видос будет у вас!")

@dp.message(F.text.contains("tiktok.com"))
async def handle_tiktok_link(message: Message):
    try:
        music_path = "audio.mp3"
        video_path = "video.mp4"
        # url_tt = message.text.replace("/send_video ", "")
        url_tt = message.text
        json_tt = download_tt(url_tt)
        title = json_tt['data']['title']
        hdplay = json_tt['data']['play']
        music_title = json_tt['data']['music_info']['title']
        music_author = json_tt['data']['music_info']['author']
        music_url = json_tt['data']['music_info']['play']
        video_url = hdplay
        await download(video_url, video_path)
        await download(music_url, music_path)
        video_input = FSInputFile(video_path)
        music_input = FSInputFile(music_path)

        # Отправляем видео
        # print("Отправляю")
        if os.path.exists(video_path):
            # Получаем размер файла в байтах
            file_size = os.path.getsize(video_path)
            # Конвертируем размер в килобайты
            file_size_kb = file_size / 1024
            threshold_kb = 50 * 1024
            # Проверяем размер файла по пороговому значению
            if file_size_kb < threshold_kb:
                if title == "":
                    await bot.send_video(chat_id=message.from_user.id, video=video_input, caption=f"Скачано с помощью @tiktok_downloadcr_bot\nРазработчик бота: @ameerchik6")
                else:
                    await bot.send_video(chat_id=message.from_user.id, video=video_input, caption=f"```Описание\n{title}```\n\nСкачано с помощью @tiktok_downloadcr_bot\nРазработчик бота: @ameerchik6")
            else:
                text = escape_markdown(
                    "Видео, которое вы хотите сохранить весит более 50 Мб. Поэтому данное видео доступно для скачивания только по ссылке ниже!")
                await bot.send_message(chat_id=message.from_user.id, text=f"{text}\n\n[Скачать видео]({hdplay})", parse_mode=ParseMode.MARKDOWN_V2)
        await bot.send_audio(chat_id=message.from_user.id, audio=music_input, title=music_title, performer=music_author)

    except Exception as e:
        await message.reply(f"Не удалось отправить видео или введенная ссылка неправильная! {e}")
    finally:
        delete_file(music_path)
        delete_file(video_path)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
