# Mdisk Downloader Bot

*A Telegram MDisk Video Downloader Bot, You can watch downloaded Videos without MX player (bypass mdisk requirements)*

---

# Variables 

_You can use [config.json](https://github.com/bipinkrish/Mdisk-Downloader-Bot/blob/master/config.json) instead of ENVs_

#### Required

- `HASH` Your API Hash from my.telegram.org
- `ID` Your API ID from my.telegram.org
- `TOKEN` Your bot token from @BotFather

#### Control (optionals) 

- `AUTH` List of Authenticated User's ID seperated by a space (everyone can use the bot if it is empty)
- `BAN` List of Banned User's ID seperated by a space (everyone can use the bot if it is empty)
- `OWNER` List of Owner User's ID seperated by a space (no one is owner if it is empty)

#### Premium Features (optionals) (only use this if you have Premium Account) (both are needed if any one is set)

- `STRING` Premium User String Session
- `TEMP_CHAT` Username or ID of Chat (Channel or Group, Private, Public), both User account and Bot should have access to messages in that chat (basically a log chat but required not optional)

#### Force Join (both are needed if any one is set)

- `TARGET` Chat's ID or Username
- `LINK` Chat's joining Link 

---

# Commands

### For Normal Users

```
start - Start Message
help - List of Commands
mdisk - Usage
thumb - Reply to a Image of size less than 200KB to set it as Thumbnail
remove - Remove Thumbnail
show - Show Thumbnail
change - Change Upload Mode (Document/Stream)
```

### For Owners

_It is temporary, once bot is redoplyed or config file is deleted it will go back to default values_

```
auth - Auth a user
unauth - UnAuth a user
ban - Ban a user
unban - UnBan a user
members - see the list of Owners,Auths,Bans
```

---