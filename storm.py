import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import json
import time


intents = discord.Intents.all()
client = commands.Bot(command_prefix='~', intents=intents)
bot_role_id = "Your_Bot_Role_ID"  # Replace with your bot's role ID

#spam detector settings
SPAM_NOTIFY_CHANNEL = "Your_Spam_Notify_Channel_ID"  # Replace with your spam notify channel ID
SPAM_THRESHOLD = 5
SPAM_SECONDS = 10
SPAM_TIMEOUT = 5
spam_history = {}
ticket_users = {}


#this code tells  that bot is now ready
@client.event
async def on_ready():
  print(f'Logged in as {client.user.name}#{client.user.discriminator}')


#this code welcomes the user whenever user joins
@client.event
async def on_member_join(member):
  guild = member.guild
  channel = discord.utils.get(guild.text_channels, name="welcome")
  if channel:
    emoji = "\U0001F44B"
    pfp_url = str(member.avatar.url) if member.avatar else str(
      member.default_avatar.url)
    embed = discord.Embed(
      title=f"Hey {member.mention}, WELCOME TO PUKKU BHAI IS LIVE.",
      description="We hope you enjoy your stay.",
      color=0x00ff00)
    embed.add_field(name=":arrow_forward: Check out",
                    value="⁠PUKKU BHAI IS LIVE⁠│🗡️・in-game-rules")
    embed.add_field(name=":arrow_forward: Read 🔮〡rules",
                    value="⁠PUKKU BHAI IS LIVE⁠│📜・🔮〡rules")
    embed.add_field(name=":arrow_forward: For support",
                    value="⁠JUST DM THE MOD MAIL OR STORM")
    embed.set_thumbnail(url=pfp_url)
    embed.set_footer(
      text=":Rz_BlackHeart: Have fun in PUKKU BHAI IS LIVE :Rz_BlackHeart:")
    await channel.send(embed=embed)


#Ban Command
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
  await member.ban(reason=reason)

  await ctx.send(f'{member.display_name} has been banned.')


@ban.error
async def ban_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


#Kick Command
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f'{member.display_name} has been kicked.')

async def say_goodbye(ctx):
   await ctx.send(f'bye bye master thanks for keeping me alive may your other life will be better!')

@kick.error
async def kick_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


#mute command
@client.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str, *, reason=None):
  duration_dict = {"s": 1, "m": 60, "h": 3600}
  if duration[-1] not in duration_dict:
    await ctx.send(
      "Invalid duration string. Please specify a duration ending in 's', 'm', or 'h'."
    )
    return
  duration_val = int(duration[:-1]) * duration_dict[duration[-1]]
  # Get the muted role (create it if it doesn't exist)
  muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
  if not muted_role:
    muted_role = await ctx.guild.create_role(name='Muted')
    for channel in ctx.guild.text_channels:
      await channel.set_permissions(muted_role, send_messages=False)

  # Mute the member
  await member.add_roles(muted_role, reason=reason)
  await ctx.send(f'{member.display_name} has been muted for {duration}.')

  # Schedule the unmute_member coroutine to run after the duration
  asyncio.create_task(unmute_member(member, muted_role, duration_val))


async def unmute_member(member, muted_role, duration):
  # Wait for the duration of the mute
  await asyncio.sleep(duration)

  # Unmute the member
  await member.remove_roles(muted_role)
  await member.send(f"You have been unmuted in {member.guild.name}.")


@mute.error
async def mute_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


@client.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
  # Get the muted role
  muted_role = discord.utils.get(ctx.guild.roles, name='Muted')

  # Check if the member is muted
  if muted_role not in member.roles:
    await ctx.send(f"{member.display_name} is not currently muted.")
    return

  # Unmute the member
  await member.remove_roles(muted_role)
  await ctx.send(f"{member.display_name} has been unmuted.")


@unmute.error
async def unmute_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


#for checking the bots latency
@client.command()
async def ping(ctx):

  latency = round(client.latency * 1000)
  await ctx.send(f'Pong! Latency: {latency}ms ')


#purge command
@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int):
  await ctx.channel.purge(limit=limit + 1)
  await ctx.send(f'{limit} messages deleted by {ctx.author.mention}')


@purge.error
async def purge_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


#backupp command
@client.command()
@commands.has_permissions(administrator=True)
async def backup(ctx):
  # Get the guild object
  guild = ctx.guild

  # Initialize the backup dictionary
  backup = {}

  # Store the guild ID
  backup["guild_id"] = guild.id

  # Store the list of text and voice channels
  backup["channels"] = []
  for channel in guild.channels:
    if isinstance(channel, discord.TextChannel):
      backup["channels"].append({"type": "text", "name": channel.name})
    elif isinstance(channel, discord.VoiceChannel):
      backup["channels"].append({"type": "voice", "name": channel.name})

  # Store the list of roles
  backup["roles"] = []
  for role in guild.roles:
    backup["roles"].append({
      "name": role.name,
      "permissions": int(role.permissions.value),
      "color": role.color.value,
      "hoist": role.hoist,
      "mentionable": role.mentionable
    })

  # Save the backup to a JSON file
  with open("backup.json", "w") as f:
    json.dump(backup, f)

  # Send a confirmation message
  await ctx.send("Backup created!")


@backup.error
async def backup_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


# Restore the server channels and roles from the backup
@client.command()
@commands.has_permissions(administrator=True)
async def restore(ctx):
  with open("backup.json", "r") as f:
    backup = json.load(f)

  guild = client.get_guild(backup["guild_id"])
  duplicate_found = False  # Flag variable

  for channel_data in backup["channels"]:
    channel_type = channel_data["type"]
    channel_name = channel_data["name"]

    # Check if channel already exists
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
      duplicate_found = True
    else:
      if channel_type == "text":
        await guild.create_text_channel(channel_name)
      elif channel_type == "voice":
        await guild.create_voice_channel(channel_name)

  for role_data in backup["roles"]:
    role_name = role_data["name"]
    permissions = discord.Permissions(role_data["permissions"])
    color = discord.Color(role_data["color"])
    hoist = role_data["hoist"]
    mentionable = role_data["mentionable"]

    # Check if role already exists
    existing_role = discord.utils.get(guild.roles, name=role_name)
    if existing_role:
      duplicate_found = True
    else:
      await guild.create_role(name=role_name,
                              permissions=permissions,
                              color=color,
                              hoist=hoist,
                              mentionable=mentionable)

  if duplicate_found:
    await ctx.send("Restoration canceled. Duplicate channels or roles found.")
  else:
    await ctx.send("Server restored!")


@restore.error
async def restore(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You don't have permission to use that command.")


async def close(ctx):
  # Check if the command is sent in a ticket channel
  if ctx.channel.name.startswith('ticket-'):
    try:

      closing_message = 'Thank you for using our services. This channel will be deleted in 10 seconds.'
      await ctx.send(closing_message)
      await asyncio.sleep(10)
      ticket_users.pop(ctx.author.id)
      await ctx.channel.delete()
    except Exception as e:
      print(e)


#integrated Mod Mail Code
@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if isinstance(message.channel, discord.DMChannel):
    guild = client.get_guild(629511427618766848)
    category = discord.utils.get(guild.categories, name='TICKET HELP')

    if not category:
      category = await guild.create_category('TICKET HELP')

    overwrites = {
      guild.default_role: discord.PermissionOverwrite(read_messages=False),
      message.author: discord.PermissionOverwrite(read_messages=True)
    }
    existing_channel = discord.utils.get(guild.channels,
                                         name=f'ticket-{message.author.name}')
    if existing_channel:
      await existing_channel.send(
        f'[{message.author.mention}] {message.content}')
    else:
      channel = await category.create_text_channel(
        f'ticket-{message.author.name}', overwrites=overwrites)
      welcome_message = f'Hello {message.author.mention}, **your ticket has been created! A staff member will be with you shortly.**\nYou can use the command "***close**" to close this ticket.'
      await message.author.send(
        f'Your ticket has been created in {channel.mention}')
      await channel.send(welcome_message)

  #mutes the user who sends the link
  await client.process_commands(message)
  if "http" in message.content:
    # Check if the user who sent the message has the necessary permissions
    if message.author.guild_permissions.administrator:
      # If the user has the necessary permissions, do not delete the link
      return
    else:
      # Otherwise, delete the link and inform the channel
      await message.delete()
      await message.channel.send(
        f"{message.author.mention} attempted to send a link, which is not allowed."
      )
      return
  author = message.author
  channel = message.channel

  author = message.author
  channel = message.channel

  #my spam logic code
  if message.author.bot:
    return

  user_id = message.author.id
  current_time = time.time()

  user_history = spam_history.get(user_id, [])
  user_history = [t for t in user_history if t > current_time - SPAM_SECONDS]
  user_history.append(current_time)
  spam_history[user_id] = user_history
  if len(user_history) > SPAM_THRESHOLD:

    remaining_time = int(user_history[0] + SPAM_SECONDS - current_time)

    await message.channel.send(
      f"{message.author.mention} Please don't spam! You will be timed out for {remaining_time} seconds."
    )

    timeout_role = discord.utils.get(message.guild.roles, name='Muted')
    await message.author.add_roles(timeout_role)
    time.sleep(SPAM_SECONDS)
    await message.author.remove_roles(timeout_role)


    #rules command
@client.command()
@commands.has_permissions(administrator=True)
async def rules(ctx):

  rules = [
    ":rotating_light: Server Rules :rotating_light:"
    ":arrow_right: Strictly no politics or religion in the chat - Keep it neutral."
    ":arrow_right: Keep it respectful - No hate speech, racism, sexism, homophobia, or disrespect. Any of which will result in a ban and will not be tolerated."
    ":arrow_right: Absolutely no NSFW - Send this to your friends, not here. Any post will result in a ban and will not be tolerated."
    ":arrow_right: Listen to Admins, Mods, or Players - If they say stop, stop."
    ":arrow_right: Do not harass players or content creators - If they want to lurk, let them. Don't scare them off."
    ":arrow_right: We all wish we could be Bjergsen, but impersonations are not acceptable - Keep nicknames and profile pictures clear of any impersonations."
    ":arrow_right: The server language is Hindi & English - Please keep the language to English & Hindi."
    ":arrow_right: Never mention @owner & any other username from Management - Unless they're talking in chat. They're here to have fun, not be harassed."
    ":arrow_right: We only ping everyone for announcements and YouTube content that has meaning behind it - deal with it."
    ":arrow_right: This is a Discord led by Mod, for the FANS. This is not the place to 'tryout'. Want to be a pro? Grind the game you love."
    ":arrow_right: If someone is found abusing staff, mods, or any normal member, they will be server muted for 1 day."
  ]

  embed = discord.Embed(title="Server Rules",
                        description="\n".join(rules),
                        color=discord.Color.green())
  embed.set_author(name="Discord Rules",
                   icon_url="https://i.imgur.com/URVlJl6.png")
  embed.set_footer(text="Be respectful, have fun, and enjoy the server!")
  await ctx.send(embed=embed)



client.run('Your_Bot_Token')  # Replace with your bot's token
