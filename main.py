import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import types
from aiogram import F
from aiogram.enums import ParseMode
import asyncio
import requests
import os
import shutil
import re
from background import keep_alive
import time

keep_alive()


def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


def download_tt(url_tiktok):
    url = "https://www.tikwm.com/api/"
    payload = {
        'url': f"{url_tiktok}",
        'count': 12,
        'cursor': 0,
        'web': 1,
        'hd': 1
    }

    response = requests.get(url, params=payload)
    response_json = response.json()['data']
    return response_json

def download_inst(url_inst):
    url = 'https://social.ioconvert.com/instagram'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'ru,ru-RU;q=0.9,en;q=0.8,uz;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://igdown.net',
        'Referer': 'https://igdown.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    payload = {
        'url': url_inst,
        'obj': 'reels',
        'language': 'en'
    }

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()['data']
    key = data['key']

    if "video" in data:
        type = "video"
        items = [item['id'] for item in data[type]['all']]
    else:
        type = "images"
        items = [item['id'] for item in data[type]]
    medias = []
    for item in items:
        download_url = f"https://social.ioconvert.com/download?obj=reels&key={key}&type={type}&id={item}&download=1&file_prefix=igDown&target_id="
        medias.append(download_url)
    return medias

# title = response_json['data']['title']
# hdplay = response_json['data']['play']
# print("Title:", title)
# print("HD Play URL:", hdplay)


# Введите сюда токен вашего бота

# BOT_TOKEN = '6846762920:AAFYPWrc16abK9CK-oHknshcn22tiZAqkpE'
BOT_TOKEN = '6308423351:AAEdjuR5wMid8ovw8QOZn6jEGC4gz9nqm44'  # kino poisk


# Идентификатор чата
# CHAT_ID = '5527705092'
# URL видео
# video_url = "tiktok_videos/video.mp4"
# video_url = "D:\Desktop\cru\\tiktok_videos\\video.mp4"


logging.basicConfig(level=logging.INFO)


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def download(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
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
            shutil.rmtree(path)
        else:
            pass
    except Exception as e:
        print(f"Не удалось удалить папку {path}: {e}")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(f"Добро пожаловать!\n\nВы можете скинуть мне ссылку на пост TikTok откуда нужно выгрузить видео и текст — через пару секунд этот видос будет у вас!")


@dp.message(F.text.contains("tiktok.com"))
async def handle_tiktok_link(message: Message):
    dev_link_escaped = escape_markdown(
        "Скачано с помощью @tiktok_downloadcr_bot\nРазработчик бота: @ameerchik6")
    dev_link = "Скачано с помощью @tiktok_downloadcr_bot\nРазработчик бота: @ameerchik6"
    try:
        user_id = message.from_user.id
        music_path = f"id{user_id}/audio.mp3"
        video_path = f"id{user_id}/video.mp4"

        # url_tt = message.text.replace("/send_video ", "")
        url_tt = message.text

        json_tt = download_tt(url_tt)
        # print(json_tt)
        # print(json_tt)
        # json_tt = download_tt(url_tt)
        # if 'images' in json_tt:
        #     images_urls = json_tt['images']
        #     # print(len(images_urls))
        #     # for i in range(len(images_urls)):
        #     #     images_path = f"id{user_id}/{i}.jpg"
        #     #     print(images_urls[i])
        #     #     download(images_urls[i], images_path)
        #     print(images_urls)
        title = json_tt['title']
        # print("title: ", title)
        play = json_tt['play']
        hdplay = json_tt['hdplay']
        music_title = json_tt['music_info']['title']
        music_author = json_tt['music_info']['author']
        music_url = "https://www.tikwm.com/" + \
            json_tt['music']
        video_url = "https://www.tikwm.com/" + play
        videohd_url = "https://www.tikwm.com/" + hdplay
        await download(video_url, video_path)
        await download(music_url, music_path)
        video_input = FSInputFile(video_path)
        music_input = FSInputFile(music_path)

        # Отправляем видео
        # print("Отправляю")
        if 'images' in json_tt:
            images = json_tt['images']
            a = 1
            for img in images:
                img_path = f"id{user_id}/img/{a}.jpeg"
                await download(img, img_path)
                a += 1
            dev_link = f"```Описание\n{escape_markdown(title)}```\n\n{dev_link_escaped}"
            media_group = MediaGroupBuilder(caption=dev_link)

            b = 1
            c = 1
            for i in range(a-1):
                img_path = f"id{user_id}/img/{b}.jpeg"
                media_group.add(
                    type="photo",
                    media=FSInputFile(path=img_path),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                b += 1
                c += 1
                if c == 11:
                    await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
                    media_group = MediaGroupBuilder(caption=dev_link)
                    c = 1
                # time.sleep(1)
            await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
        else:
            if os.path.exists(video_path):
                # Получаем размер файла в байтах
                file_size = os.path.getsize(video_path)
                # Конвертируем размер в килобайты
                file_size_kb = file_size / 1024
                threshold_kb = 50 * 1024
                # Проверяем размер файла по пороговому значению
                if file_size_kb < threshold_kb:
                    if title == "":
                        await bot.send_video(chat_id=message.chat.id, video=video_input, caption=f"Скачать видео в [hd]({videohd_url})\n\n{dev_link_escaped}", parse_mode=ParseMode.MARKDOWN_V2)
                    else:
                        await bot.send_video(chat_id=message.chat.id, video=video_input, caption=f"```Описание\n{escape_markdown(title)}```\nСкачать видео в [hd]({videohd_url})\n\n{dev_link_escaped}", parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    text = escape_markdown(
                        "Видео, которое вы хотите сохранить весит более 50 Мб. Поэтому данное видео доступно для скачивания только по ссылке ниже!")
                    await bot.send_message(chat_id=message.chat.id, text=f"{text}\nСкачать видео в [hd]({videohd_url})\n\n[Скачать видео]({video_url})", parse_mode=ParseMode.MARKDOWN_V2)
        await bot.send_audio(chat_id=message.chat.id, audio=music_input, title=music_title, performer=music_author)
        # elif images_urls:
        #     print("Есть!")

    except Exception as e:
        print(e)
        await message.reply(f"Не удалось отправить видео или введенная ссылка неправильная!")
    finally:
        pass
        delete_file(f"id{user_id}")


async def inst_download(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type')
                if content_type:
                    if 'image/jpeg' in content_type:
                        extension = '.jpg'
                    elif 'image/png' in content_type:
                        extension = '.png'
                    elif 'image/gif' in content_type:
                        extension = '.gif'
                    elif 'image/webp' in content_type:
                        extension = '.webp'
                    elif 'video/mp4' in content_type:
                        extension = '.mp4'
                    elif 'application/pdf' in content_type:
                        extension = '.pdf'
                    elif 'text/html' in content_type:
                        extension = '.html'
                    else:
                        extension = ''
                else:
                    extension = ''

                # Проверяем, есть ли уже расширение в path
                if not path.endswith(extension):
                    save_path = f"{path}{extension}"
                else:
                    save_path = path

                with open(save_path, 'wb') as f:
                    f.write(await response.read())
                    print(f"Скачалось: {save_path}")
            else:
                raise Exception(f"Failed to download file, status code: {response.status}")


@dp.message(F.text.contains("instagram.com"))
async def handle_instagram_link(message: Message):
    dev_link = "Скачано с помощью @tiktok_downloadcr_bot\nРазработчик бота: @ameerchik6"
    try:
        medias = download_inst(message.text)
        print(medias)
        user_id = message.from_user.id
        
        if medias:
            a = 1
            for media in medias:
                img_path = f"id{user_id}/media{a}"
                await inst_download(media, img_path)
                a += 1
            media_group = MediaGroupBuilder(caption=dev_link)

            b = 1
            c = 1
            for i in range(a-1):
                img_path = f"id{user_id}/media{b}.jpg"
                video_path = f"id{user_id}/media{b}.mp4"
                if os.path.exists(img_path):
                    # print(img_path)
                    media_group.add(
                        type="photo",
                        media=FSInputFile(path=img_path)
                    )
                elif os.path.exists(video_path):
                    print(video_path)
                    media_group.add(
                        type="video",
                        media=FSInputFile(path=video_path)
                    )
                b += 1
                c += 1
                if c == 11:
                    await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
                    media_group = MediaGroupBuilder(caption=dev_link)
                    c = 1
            await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
        
    except Exception as e:
        print(e)
        await message.reply(f"Не удалось отправить видео или введенная ссылка неправильная!")
    finally:
        pass
        delete_file(f"id{user_id}")


async def main():
    await bot.send_message(chat_id=5527705092, text="Бот заработало!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
