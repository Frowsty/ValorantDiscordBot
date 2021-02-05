# ValorantDiscordBot
A quite barebone bot that will automatically verify users rank (Created specifically for Valorant Curios discord server)

Current commands:
(prefix is ",")
## Mod commands 
restartBot - Will issue a restart on the bot which causes it to reload the python script thus applying any update that was uploaded to the server
pauseBot   - As the name suggests it pauses the bot from listening to any commands (other than mod allowed commands such as restart, pause, resume)
resumeBot  - Will resume the bot if bot is in a paused state

## User commands
registerAccount - Will start a login process in DMs to achieve access to valorant ranked data through the official valorant API
assignRole      - Will assign the correct role correlating to whichever rank you are in valorant (Only for Diamond and above)
