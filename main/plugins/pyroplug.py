# Github.com/Vasusen-code

from .. import bot as Drone
import asyncio, time, os

from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot, findVideoResolution
from main.plugins.helpers import duration as dr

from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid
from pyrogram.enums import MessageMediaType
from ethon.pyfunc import video_metadata
from ethon.telefunc import fast_upload
from moviepy.editor import VideoFileClip
from telethon.tl.types import DocumentAttributeVideo
from telethon import events

def thumbnail(sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    else:
         return None
    
async def check(userbot, client, link):
    msg_id = int(link.split("/")[-1])
    if 't.me/c/' in link:
        try:
            chat = int('-100' + str(link.split("/")[-2]))
            await userbot.get_messages(chat, msg_id)
            return True, None
        except ValueError:
            return False, "**Invalid Link!**"
        except Exception:
            return False, "Have you joined the channel?"
    else:
        try:
            chat = str(link.split("/")[-2])
            await client.get_messages(chat, msg_id)
            return True, None
        except Exception:
            return False, "Maybe bot is banned from the chat, or your link is invalid!"
            
async def get_msg(userbot, client, bot, sender, to, edit_id, msg_link, i):
    edit = ""
    chat = ""
    round_message = False
    msg_id = int(msg_link.split("/")[-1]) + int(i)
    height, width, duration, thumb_path = 90, 90, 0, None
    if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
        if 't.me/b/' in msg_link:
            chat = str(msg_link.split("/")[-2])
        else:
            chat = int('-100' + str(msg_link.split("/")[-2]))
        file = ""
        try:
            msg = await userbot.get_messages(chat, msg_id)
            print(msg)
            if msg.media:
                if msg.media==MessageMediaType.WEB_PAGE:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(to, msg.text.markdown)
                    await edit.delete()
                    return
            if not msg.media:
                if msg.text:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(to, msg.text.markdown)
                    await edit.delete()
                    return
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**DOWNLOADING:**\n",
                    edit,
                    time.time()
                )
            )
            print(file)
            await edit.edit('Preparing to Upload!')
            caption = None
            if msg.caption is not None:
                caption = msg.caption
            if msg.media==MessageMediaType.VIDEO_NOTE:
                round_message = True
                print("Trying to get metadata")
                data = video_metadata(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                await client.send_video_note(
                    chat_id=to,
                    video_note=file,
                    length=height, duration=duration, 
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            elif msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                print("Trying to get metadata")
                data = video_metadata(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                await client.send_video(
                    chat_id=to,
                    video=file,
                    caption=caption,
                    supports_streaming=True,
                    height=height, width=width, duration=duration, 
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            
            elif msg.media==MessageMediaType.PHOTO:
                await edit.edit("Uploading photo.")
                await bot.send_file(to, file, caption=caption)
            else:
                thumb_path=thumbnail(sender)
                await client.send_document(
                    to,
                    file, 
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            try:
                os.remove(file)
                if os.path.isfile(file) == True:
                    os.remove(file)
            except Exception as e:
                print(e)
            await edit.delete()
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Have you joined the channel?")
            return
        except Exception as e:
            print(e)
            if "messages.SendMedia" in str(e): 
                try: 
                    if msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)] 
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    elif msg.media==MessageMediaType.VIDEO_NOTE:
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)] 
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    else:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, force_document=True)
                    if os.path.isfile(file) == True:
                        os.remove(file)
                except Exception as e:
                    print(e)
                    await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
                    try:
                        os.remove(file)
                    except Exception:
                        return
                    return 
            elif "SaveBigFilePartRequest" in str(e):
                try: 
                    if msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)] 
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    elif msg.media==MessageMediaType.VIDEO_NOTE:
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)] 
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    else:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, force_document=True)
                    if os.path.isfile(file) == True:
                        os.remove(file)
                except Exception as e:
                    print("Telethon tried but failed!")
                    print(e)
                    await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
                    try:
                        os.remove(file)
                    except Exception:
                        return
                    return 
            else:
                await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
                try:
                    os.remove(file)
                except Exception:
                    return
                return
        try:
            os.remove(file)
            if os.path.isfile(file) == True:
                os.remove(file)
        except Exception as e:
            print(e)
        await edit.delete()
    else:
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat =  msg_link.split("/")[-2]
        try:
            await client.copy_message(to, chat, msg_id)
        except Exception as e:
            print(e)
            return await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
        await edit.delete()
        
async def get_bulk_msg(userbot, client, sender, chat, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    await get_msg(userbot, client, Drone, sender, chat, x.id, msg_link, i)
