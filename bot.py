import discord
import datetime
import os
import requests
import json
import sys
import time
from locale import atoi, setlocale, LC_NUMERIC
import valorantApi

setlocale(LC_NUMERIC, 'en_US.UTF8')
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

botAdmins = [154670731354046464]
usersBeingVerified = dict()

pauseBot = False
restartedBot = False
restartCommandChannel = ""
savedGuildID = 0
restartTime = 0

startTime = time.time()

curPath = os.path.dirname(sys.argv[0])

if not os.path.exists(os.path.join(curPath, "servers")):
    print("There is no directory called servers")
    os.mkdir(os.path.join(curPath, "servers"))

if os.path.exists("restartBot.txt"):
    with open("restartBot.txt", 'r') as f:
        restartBotText = ""
        for line in f.readlines():
            restartBotText = restartBotText + line
        if len(restartBotText) > 1:
            splitRestartBotText = restartBotText.split(' ')
            if splitRestartBotText[0] == "TRUE":
                restartedBot = True
                restartCommandChannel = splitRestartBotText[1]
                savedGuildID = int(splitRestartBotText[2])
                restartTime = float(splitRestartBotText[3])

def addModsToAdminList():
    for guild in client.guilds:
        for member in guild.members:
            currentRoles = [role.name for role in member.roles]
            if "moderator" in currentRoles or "admin" in currentRoles:
                botAdmins.append(member.id)

def findRankInMatchHistory(data):
    rank = 0
    for match in data["Matches"]:
        if match["TierAfterUpdate"] > 0 and rank == 0:
            rank = match["TierAfterUpdate"]
    return rank

def saveDataToServer(message, guild, data, gamename):
    if not os.path.exists(os.path.join(curPath, "servers", str(guild))):
        os.mkdir(os.path.join(curPath, "servers", str(guild)))
    jsonData = {}
    with open(os.path.join(curPath, "servers", str(guild), "UserData.json"), "r") as f:
        try:
            jsonData = json.load(f)
        except:
            print("JSON failed to load, file is most likely missing!")

    with open(os.path.join(curPath, "servers", str(guild), "UserData.json"), "w") as f:
        if str(message.author.id) in jsonData:
            jsonData[str(message.author.id)]["gameName"] = gamename
            jsonData[str(message.author.id)]["rankID"] = str(findRankInMatchHistory(data))
        else:
            jsonData[str(message.author.id)] = {"gameName": gamename, "rankID": str(findRankInMatchHistory(data))}

        json.dump(jsonData, f, indent=4)

def removeUserFromDict(d, key):
    r = dict(d)
    del r[key]
    return r

@client.event
async def on_ready():
    global restartedBot
    global restartCommandChannel
    global restartTime

    print('Connected as {0.user}'.format(client))
    # If bot was restarted
    if restartedBot:
        guild = client.get_guild(savedGuildID)
        channel = discord.utils.get(guild.text_channels, name=restartCommandChannel)
        if os.path.exists("restartBot.txt"):
            os.remove("restartBot.txt")
            restartedBot = False
            restartCommandChannel = ""
        await channel.send("Bot restarted successfully! (Duration: {0} seconds)".format(round(time.time() - restartTime, 2)))
    for guild in client.guilds:
        if not os.path.exists(os.path.join(curPath, "servers", str(guild.id))):
            os.mkdir(os.path.join(curPath, "servers", str(guild.id)))
    addModsToAdminList()

@client.event
async def on_message(message):
    global pauseBot
    global restartedBot
    global restartCommandChannel
    global startTime
    global usersBeingVerified

    #if message.author == client.user or message.channel.id != 731635793927340165:
    #    return
    if message.author == client.user:
        return
    if message.content.startswith(',adminHelp') and message.author.id in botAdmins:
        replyMessage = '<@{}>'.format(message.author.id)
        replyMessage = replyMessage + "```***Help / Commands for owner***\n"
        replyMessage = replyMessage + ",restartBot    - Restart the bot, will take a few seconds. Please notify Frosty#0186 to execute this command.\n"
        replyMessage = replyMessage + ",pauseBot      - Pause the bot from responding to commands, will still respond to admin commands\n"
        replyMessage = replyMessage + ",resumeBot     - Unpause the bot from responding to commands```"
        print("{0} executed admin help commands".format(message.author))
        await message.channel.send(replyMessage)
    elif message.content.startswith(',adminHelp'):
        replyMessage = '<@{}>'.format(message.author.id)
        replyMessage = replyMessage + "```***Error***\nYou can only access this command if you're admin of the bot```"
        await message.channel.send(replyMessage)
      
    if message.content.startswith(',pauseBot') and message.author.id in botAdmins:
        pauseBot = True
        print("{0} executed pause bot command".format(message.author))
        await message.channel.send("Bot paused!")

    if message.content.startswith(',resumeBot') and message.author.id in botAdmins:
        pauseBot = False
        print("{0} executed unpause bot command".format(message.author))
        await message.channel.send("Bot resumed!")

    if message.content.startswith(',restartBot') and message.author.id in botAdmins :
        if os.path.exists("restartBot.txt"):
            os.remove("restartBot.txt")
        with open("restartBot.txt", 'w') as f:
            print("Saved channel and guild")
            f.write("TRUE " + message.channel.name + " " + str(message.guild.id) + " " + str(time.time()))
        print(f"{message.author} has executed a restart!")
        await message.channel.send("Please wait a moment as I restart! Be right back!")
        os.execv(sys.executable, ['python3'] + sys.argv)
    elif message.content.startswith(',restartBot'):
        await message.channel.send("You lack permissions to execute a restart! Please provide the root password or become owner of the bot")
    # End of root access

    if not message.author.id in usersBeingVerified and not message.channel.name == "rank-proof":
        return

    # List all commands and explanation for the command
    if not pauseBot:
        if message.content.startswith(',help'):
            replyMessage = '<@{}>'.format(message.author.id)
            replyMessage = replyMessage + "```***Help / Commands***\n"
            replyMessage = replyMessage + ",registerAccount - Will take you through a login sequence through DMs (required step in order to run ,assignRole command)\n"
            replyMessage = replyMessage + ",assignRole      - Will assign the role depending on the your rank in valorant (only diamond or above)```"
            print("{0} executed help command".format(message.author))
            await message.channel.send(replyMessage)
        
        if message.author.id in usersBeingVerified:
            if usersBeingVerified[message.author.id]["state"] == "username":
                usersBeingVerified[message.author.id]["username"] = message.content
                await message.author.send("Please enter your password (passwords are not saved): ")
                usersBeingVerified[message.author.id]["state"] = "password"
            elif usersBeingVerified[message.author.id]["state"] == "password":
                usersBeingVerified[message.author.id]["password"] = message.content
                await message.author.send("Please enter your region (EU/NA/AP/KO): ")
                usersBeingVerified[message.author.id]["state"] = "region"
            elif usersBeingVerified[message.author.id]["state"] == "region":
                usersBeingVerified[message.author.id]["region"] = message.content
                valorant = valorantApi.ValorantAPI(usersBeingVerified[message.author.id]["username"], usersBeingVerified[message.author.id]["password"], usersBeingVerified[message.author.id]["region"])
                if not valorant.game_name == "Error":
                    usersBeingVerified[message.author.id]["data"] = valorant.get_match_history()
                    usersBeingVerified[message.author.id]["gamename"] = valorant.game_name
                    if usersBeingVerified[message.author.id]["data"] != "Error":
                        saveDataToServer(message, usersBeingVerified[message.author.id]["guild"], usersBeingVerified[message.author.id]["data"], usersBeingVerified[message.author.id]["gamename"])
                    usersBeingVerified = removeUserFromDict(usersBeingVerified, message.author.id)
                    print(f"{message.author} ({message.author.id}) has finished the registration process")
                    await message.author.send("Your ranked data has been saved and all login information has been cleared (Close DMs from this bot or delete messages containing your password to avoid someone seeing it)")
                else:
                    usersBeingVerified = removeUserFromDict(usersBeingVerified, message.author.id)
                    await message.author.send("Login error has occured, make sure everything was entered correctly and restart the sign in process by executing the ,registerAccount command in the server again!")

        if message.content.startswith(",registerAccount"):
            if not message.author.id in usersBeingVerified:
                await message.author.send("Please enter your username: ")
                usersBeingVerified[message.author.id] = {"state": "", "username": "", "password": "", "region": "", "data": None, "guild": None, "gamename": None}
                usersBeingVerified[message.author.id]["state"] = "username"
                usersBeingVerified[message.author.id]["guild"] = message.guild.id
                print(f"{message.author} ({message.author.id}) has started the registration process")
                await message.channel.send("Login process has started, Check your DMs!")

        if message.content.startswith(",assignRole"):
            userID = message.author.id
            member = message.guild.get_member(int(userID))
            if os.path.exists(os.path.join(curPath, "servers", str(message.guild.id))):
                try:
                    with open(os.path.join(curPath, "servers", str(message.guild.id), "UserData.json"), "r") as f:
                        jsonData = json.load(f)
                        gameName = jsonData[str(userID)]["gameName"]
                        rankNumber = jsonData[str(userID)]["rankID"]
                        rankList = requests.get("https://502.wtf/ValorrankInfo.json")
                        rankList = rankList.json()
                        rankName = rankList["Ranks"][str(rankNumber)]
                        role = None
                        currentRoles = [role.name for role in member.roles]
                        assignedRole = "User is not above Diamond, please assign your role manually in the #rank-assign channel"
                        if "Diamond" in rankName:
                            role = discord.utils.get(member.guild.roles, name="Diamond")
                        elif "Immortal" in rankName:
                            role = discord.utils.get(member.guild.roles, name="Immortal")
                        elif "Radiant" in rankName:
                            role = discord.utils.get(member.guild.roles, name="Radiant")

                        if role:
                            assignedRole = role.name
                            if not assignedRole in currentRoles:
                                await member.add_roles(role)
                                replyMessage = '<@{}>'.format(message.author.id) + "```***Rank of Discord User {} (ID: {})***\nGame name: {}\nPlayer rank: {} \n\nUser was assigned the {} role```".format(message.author, userID, gameName, rankName, assignedRole)
                            else:
                                replyMessage = '<@{}>'.format(message.author.id) + "```***Rank of Discord User {} (ID: {})***\nGame name: {}\nPlayer rank: {} \n\nUser already has correct role assigned```".format(message.author, userID, gameName, rankName)
                            if assignedRole == "Radiant" and "Diamond" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Diamond")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                            if assignedRole == "Radiant" and "Immortal" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Immortal")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                            if assignedRole == "Immortal" and "Radiant" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Radiant")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                            if assignedRole == "Immortal" and "Diamond" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Diamond")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                            if assignedRole == "Diamond" and "Platinum" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Platinum")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                            if assignedRole == "Immortal" and "Platinum" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Platinum")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                            if assignedRole == "Radiant" and "Platinum" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Platinum")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                           
                            # Assign a verified role to the user
                            verifyRole = discord.utils.get(member.guild.roles, name="Verified EP2")
                            if verifyRole:
                                await member.add_roles(verifyRole)

                            if "Proof request" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Proof request")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                                    await message.author.send("You were assigned the {} role (Close DMs from this bot or delete messages containing your password to avoid someone seeing it)".format(rankName))
                            print(f"{message.author} ({message.author.id}) has succcessfully finished the rank proof process and was assigned a role")
                        else:
                            if "Proof request" in currentRoles:
                                removeRole = discord.utils.get(member.guild.roles, name="Proof request")
                                if removeRole:
                                    await member.remove_roles(removeRole)
                                    await message.author.send("Only Diamond or above is eligible for rank-proof (Close DMs from this bot or delete messages containing your password to avoid someone seeing it)".format(rankName))

                            replyMessage = '<@{}>'.format(message.author.id) + f"```{assignedRole}```"
                            print(f"{message.author} ({message.author.id}) Not eligible for rank-proof, user was denied!")
                except FileNotFoundError: 
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Error***\nRanked data not found, make sure the account is registered by using ,registerAccount```'
                except KeyError:
                    replyMessage = '<@{}>'.format(message.author.id) + '```***Error***\nRanked data not found, make sure the account is registered by using ,registerAccount```'
            await message.channel.send(replyMessage)

botToken = None
if os.path.exists("token.txt"):
    with open("token.txt", 'r') as f:
        botToken = f.readline()

if botToken:
    print("Bot token found inside token.txt, launching bot!")
    client.run(botToken)
else:
    print("Bot token not found, exiting bot!")