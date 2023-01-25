# Mdisk Downloader Bot

*A Telegram MDisk Video Downloader Bot, You can watch downloaded Videos without MX player (bypass mdisk requirements)*

---

# Variables

#### Required

- `HASH` Your API Hash from my.telegram.org
- `ID` Your API ID from my.telegram.org
- `TOKEN` Your bot token from @BotFather

#### Optionals (everyone can use the bot if it is empty)

- `WIN` Set to 1 to use Windows version, defaults to 0 which is for Linux version
- `AUTH` List of Authenticated User's ID seperated by comma (,)
- `BAN` List of Banned User's ID seperated by comma (,)

#### Premium Features (upto 4 GB Files) (Only use this if you have Premium Account)

- `STRING` Premium User String Session
- `TEMP_CHAT` Username or ID of Chat (Channel or Group, Private, Public), both User account and Bot should have access to messages in that chat (basically a log chat but required not optional)

---

# Usage

```
/start - start message
/help - list of commands
/mdisk mdisklink - usage
/thumb - reply to a image document of size less than 200KB to set it as Thumbnail
( you can also send image as a photo to set it as Thumbnail automatically )
/remove - remove Thumbnail
/show - show Thumbnail
/change - change upload mode
( default mode is Document )
```
---

# Deploy

*You can use the bot locally by either running* **main.py** or deploy using **Procfile** or **Dokerfile** or **docker-compose.yml**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/D6ueVa?referralCode=_4oAwx)
