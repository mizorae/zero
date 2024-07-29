import discord 
from discord.ext import commands
from discord import Embed
import os
import asyncio
import random
import time


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "request.png")


TOKEN ='MTIzNDAyMzQ0MzQ2NTUwMjc1Mw.Gg43ah.BW9tjE-htb4Wsnl5H3664r1iYlDeFxn0z06nok'

intents = discord.Intents.all()



client = discord.Client(intents=intents)
client = commands.Bot(command_prefix = '.', intents=intents)

import discord
from discord.ext import commands
import asyncio

# Define the bot's prefix
client = commands.Bot(command_prefix='.', intents=intents)

@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def app(ctx):
    try:
        # Check if the command was invoked in a DM channel
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Please continue this request in DMs. I've sent you a message!")
            # Attempt to send the DM
            try:
                await ctx.author.send(embed=embed_prompt)
            except discord.Forbidden:
                await ctx.send("I couldn't send you a DM. Please allow DMs from server members.")
                return
        
        # Your command logic here
        questions = [
            "Do you meet basics?",
            "What is your username?",
            "Link to your socials",
            "What do you edit on?",
            "Link to your edit"
        ]
        answers = []
        
        for question in questions:
            embed_question = discord.Embed(title="Question", color=discord.Color.from_rgb(0, 0, 0))  # Black color
            embed_question.description = question
            await ctx.author.send(embed=embed_question)
            
            try:
                response = await client.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
                answers.append(response.content)
            except asyncio.TimeoutError:
                await ctx.author.send("You took too long to respond. Please restart the application.")
                return
        
        # Check if answers list is empty
        if not answers:
            await ctx.author.send("Your request is incomplete. Please provide answers to all questions.")
            return
        
        # Get the user ID and username
        user_id = str(ctx.author.id)
        username = ctx.author.name

        # Get the specific channel using the channel ID
        channel = ctx.guild.get_channel(1261511543120461854)
        if channel is None:
            await ctx.send("Error: The designated channel could not be found.")
            return
        
        # Send a message to ping the role
        role_ping_message = (
            f"<@&1261510675415695452> A new application has been submitted. "
            "Please review it."
        )
        await channel.send(role_ping_message)

        # Construct the embed message for the user's answers
        embed_answers = discord.Embed(title="New Application", color=discord.Color.from_rgb(0, 0, 0))  # Black color
        embed_answers.add_field(name="User", value=f"{username} ({user_id})")
        for question, answer in zip(questions, answers):
            embed_answers.add_field(name=question, value=answer, inline=False)

        # Send the embed message to the specified channel
        await channel.send(embed=embed_answers)

        # Inform the user that the request has been sent to the moderators
        embed_thanks = discord.Embed(
            title="Thank You!",
            description="Thank you for applying to **zero.**, we wish you the best of luck. Make sure to look into the <#1261511543120461854> channel for your results. :)",
            color=discord.Color.from_rgb(0, 0, 0)  # Black color
        )
        await ctx.author.send(embed=embed_thanks)

        # React with check mark if able to DM
        await ctx.message.add_reaction("✅")

    except discord.Forbidden:
        # React with X if unable to DM and send an error message
        await ctx.message.add_reaction("❌")
        await ctx.send("Error: I couldn't send you a DM. Please allow DMs from server members.")
    except asyncio.TimeoutError:
        await ctx.send("Error: Please wait at least 10 seconds before using this command again.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Embed prompt to answer questions
embed_prompt = discord.Embed(
    title="Request Information",
    description="Please answer the following questions:",
    color=discord.Color.from_rgb(0, 0, 0)  # Black color
)


@client.command()
@commands.has_permissions(manage_messages=True)
async def close(ctx):
    # Store the name of the ticket channel
    channel_name = ctx.channel.name

    # Delete the ticket channel
    await ctx.channel.delete()

    # Send a closure message to all members in the channel
    closure_message = f"The ticket channel **{channel_name}** has been closed. If you have any further questions, feel free to open a new ticket."
    if closure_message:
        # Find a suitable channel to send the message
        target_channel = ctx.channel.guild.system_channel or ctx.author.dm_channel

        if target_channel:
            await target_channel.send(closure_message)
        else:
            print("No suitable channel found to send the closure message.")

    # Log the command in the log channel
    log_channel = discord.utils.get(ctx.guild.channels, name="log-channel")
    if log_channel:
        embed = discord.Embed(
            title="Ticket Closed",
            description=f"The ticket channel **{channel_name}** was closed by {ctx.author.mention}.",
            color=discord.Color.from_rgb(87, 36, 36)
        )
        await log_channel.send(embed=embed)

ticket_category_name = "other-support"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    # Set the bot's presence
    activity = discord.Activity(name="zero | .", type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)

@client.command()
async def support(ctx):
    # Check if the user has an existing ticket
    existing_ticket = discord.utils.get(ctx.guild.text_channels, name=f"ticket-{ctx.author.id}")
    if existing_ticket:
        await ctx.send("You already have an existing support ticket.")
        return

    # Check if the support category exists, if not create it
    support_category = discord.utils.get(ctx.guild.categories, name=ticket_category_name)
    if support_category is None:
        support_category = await ctx.guild.create_category(name=ticket_category_name)

    # Create a ticket channel under the support category
    ticket_channel_name = f"ticket-{ctx.author.id}"
    ticket_channel = await support_category.create_text_channel(name=ticket_channel_name)

    # Add permissions for the user and bot in the ticket channel
    await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    await ticket_channel.set_permissions(ctx.guild.me, read_messages=True, send_messages=True)

    # Send a message in the ticket channel
    await ticket_channel.send(f"Support ticket created by {ctx.author.mention}. Please state your issue.")

@client.event
async def on_message(message):
    # Check if the message is in a ticket channel and sent by the ticket creator
    if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-") and message.channel.topic == str(message.author.id):
        # Process the message as needed
        await message.channel.send("Your message has been received.")
    else:
        await client.process_commands(message)

@client.command()
@commands.has_permissions(administrator=True)
async def announce(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # Prompt for the title
        embed = discord.Embed(title="Announcement", description="Please enter the title of the announcement:", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        title = await client.wait_for('message', check=check, timeout=60)
        title = title.content

        # Prompt for the description
        embed = discord.Embed(title="Announcement", description="Please enter the description of the announcement:", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        description = await client.wait_for('message', check=check, timeout=60)
        description = description.content

        # Prompt for the image URL
        embed = discord.Embed(title="Announcement", description="Please enter the image URL for the announcement (type 'none' if you don't want an image):", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        image_url = await client.wait_for('message', check=check, timeout=60)
        image_url = image_url.content

        # Prompt for the color
        embed = discord.Embed(title="Announcement", description="Please enter the color for the announcement (in hexadecimal format, e.g., #RRGGBB):", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        color = await client.wait_for('message', check=check, timeout=60)
        color = int(color.content.strip('#'), 16)

        # Prompt for the footer
        embed = discord.Embed(title="Announcement", description="Please enter the footer for the announcement:", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        footer = await client.wait_for('message', check=check, timeout=60)
        footer = footer.content

        # Prompt for the channel
        embed = discord.Embed(title="Announcement", description="Please mention the channel where you want to send the announcement (or type 'none' for the current channel):", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        channel_mention = await client.wait_for('message', check=check, timeout=60)
        if channel_mention.content.lower() == 'none':
            channel = ctx.channel
        else:
            channel = discord.utils.get(ctx.guild.channels, mention=channel_mention.content)
            if not channel:
                await ctx.send("Invalid channel mention. Announcement canceled.")
                return

        # Prompt for the ping
        embed = discord.Embed(title="Announcement", description="Do you want to ping @here, @everyone, or no ping? (Type 'here', 'everyone', or 'none'):", color=discord.Color.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        ping_input = await client.wait_for('message', check=check, timeout=60)
        ping_input = ping_input.content.lower()

        ping = None
        if ping_input == 'here':
            ping = '@here'
        elif ping_input == 'everyone':
            ping = '@everyone'

        embed = discord.Embed(title=title, description=description, color=color)
        if image_url.lower() != 'none':
            embed.set_image(url=image_url)
        embed.set_footer(text=footer)

        await channel.send(content=ping, embed=embed)
        await ctx.send("Announcement sent successfully!")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Announcement canceled.")

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if member is None:
        await ctx.send("Please specify the user to ban.")
        return

    if reason is None:
        reason = "No reason provided"

    # Attempt to send a DM to the member
    try:
        embed = discord.Embed(
            title="You have been banned",
            description=f"You have been banned from {ctx.guild.name} for the following reason:\n\n{reason}\n\nPlease message mizorea to appeal.",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        await member.send(embed=embed)
    except discord.Forbidden:
        await ctx.send(f"Could not send a DM to {member.mention}. Banning without notification.")

    # Ban the member
    await member.ban(reason=reason)

    # Send an embed message in the log channel
    log_channel = discord.utils.get(ctx.guild.channels, name="log-channel")
    if log_channel:
        embed = discord.Embed(
            title="Member Banned",
            description=f"**{member}** has been banned by **{ctx.author}** for the following reason:\n\n{reason}",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        await log_channel.send(embed=embed)

    await ctx.send(f"{member} has been banned from the server.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the user to ban.")



@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = "No reason provided"

    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked from the server. Reason: {reason}")

    # Log the kick
    log_channel = discord.utils.get(ctx.guild.channels, name="log-channel")
    if log_channel:
        embed = discord.Embed(
            title="Member Kicked",
            description=f"**{member}** has been kicked by **{ctx.author}**. Reason: {reason}",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        await log_channel.send(embed=embed)
    else:
        await ctx.send("Log channel not found. Please create a channel named 'log-channel' for logging.")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to kick members.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention the user you want to kick.")

@client.event
async def on_member_join(member):
    # Get the channel where the log will be sent
    log_channel = discord.utils.get(member.guild.channels, name="joins-leaves")

    # Calculate the account creation date
    creation_date = member.created_at.strftime("%Y-%m-%d %H:%M:%S")

    # Get the invite that was used to join (if available)
    invite = await get_invite_used(member.guild)

    # Prepare the embed message with green color
    embed = discord.Embed(
        title="Member Joined",
        color=discord.Color.green()
    )
    embed.add_field(name="Username", value=member.display_name, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)
    embed.add_field(name="Account Created On", value=creation_date, inline=False)
    if invite:
        embed.add_field(name="Invited By", value=invite.inviter.name, inline=False)
        embed.add_field(name="Invite Code", value=invite.code, inline=False)
    else:
        embed.add_field(name="Invite Code", value="Unknown (Direct Join)", inline=False)

    # Send the embed message to the log channel
    if log_channel:
        await log_channel.send(embed=embed)

@client.event
async def on_member_remove(member):
    # Get the channel where the log will be sent
    log_channel = discord.utils.get(member.guild.channels, name="joins-leaves")

    # Prepare the embed message with red color
    embed = discord.Embed(
        title="Member Left",
        color=discord.Color.red()
    )
    embed.add_field(name="Username", value=member.display_name, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)

    # Send the embed message to the log channel
    if log_channel:
        await log_channel.send(embed=embed)

async def get_invite_used(guild):
    invites = await guild.invites()
    for invite in invites:
        if invite.uses != invite.max_uses:
            return invite
    return None

@client.command()
async def serverinfo(ctx):
    guild = ctx.guild

    # Fetching various information about the server
    total_members = guild.member_count
    online_members = sum(member.status != discord.Status.offline for member in guild.members)
    roles = len(guild.roles)
    server_owner = guild.owner

    # Embed setup
    embed = discord.Embed(title="Server Information", color=discord.Color.from_rgb(0, 0, 0))
    embed.add_field(name="Server Name", value=guild.name, inline=False)
    embed.add_field(name="Owner", value=server_owner, inline=False)
    embed.add_field(name="Total Members", value=total_members, inline=True)
    embed.add_field(name="Online Members", value=online_members, inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=guild.icon.url)

    # Sending the embed
    await ctx.send(embed=embed)

staff_commands = ['announce', 'ban', 'kick', 'giveaway']
general_commands = ['req', 'support', 'serverinfo', 'botinfo']

client.remove_command('help')

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Command List", color=discord.Color.from_rgb(0, 0, 0))
    embed.add_field(name="Staff Commands", value='\n'.join(staff_commands), inline=False)
    embed.add_field(name="General Commands", value='\n'.join(general_commands), inline=False)
    await ctx.send(embed=embed)


@client.command()
async def giveaway(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    embed_prompt_channel = discord.Embed(title="Giveaway Setup", description="Please mention the channel where you want to post the giveaway:", color=discord.Color.from_rgb(0, 0, 0))
    embed_prompt_channel.set_image(url="https://cdn.discordapp.com/attachments/1234029947589365820/1234279370378444840/572424_10.png?ex=663027bd&is=662ed63d&hm=f2047257b023fdf85d1392b440bb0bfd5de17a8d75bad7d519c6c112a5d702fb&")
    await ctx.send(embed=embed_prompt_channel)

    try:
        channel_msg = await ctx.bot.wait_for('message', check=check, timeout=30)
        channel_id = int(channel_msg.content.strip("<>#"))
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            raise ValueError("Channel not found")
    except (asyncio.TimeoutError, ValueError):
        return await ctx.send("Invalid channel or timeout. Giveaway creation canceled.")

    embed_prompt = discord.Embed(title="Giveaway Setup", description="Let's set up the giveaway!\n\nPlease enter the duration of the giveaway (in seconds):", color=discord.Color.from_rgb(0, 0, 0))
    embed_prompt.set_image(url="https://cdn.discordapp.com/attachments/1234029947589365820/1234279370378444840/572424_10.png?ex=663027bd&is=662ed63d&hm=f2047257b023fdf85d1392b440bb0bfd5de17a8d75bad7d519c6c112a5d702fb&")
    await ctx.send(embed=embed_prompt)

    try:
        duration_msg = await ctx.bot.wait_for('message', check=check, timeout=30)
        duration = int(duration_msg.content)
    except asyncio.TimeoutError:
        return await ctx.send("You took too long to respond. Giveaway creation canceled.")

    embed_prompt = discord.Embed(title="Giveaway Setup", description="Please enter the prize for the giveaway:", color=discord.Color.from_rgb(0, 0, 0))
    embed_prompt.set_image(url="https://cdn.discordapp.com/attachments/1234029947589365820/1234279370378444840/572424_10.png?ex=663027bd&is=662ed63d&hm=f2047257b023fdf85d1392b440bb0bfd5de17a8d75bad7d519c6c112a5d702fb&")
    await ctx.send(embed=embed_prompt)

    try:
        prize_msg = await ctx.bot.wait_for('message', check=check, timeout=30)
        prize = prize_msg.content
    except asyncio.TimeoutError:
        return await ctx.send("You took too long to respond. Giveaway creation canceled.")

    embed_giveaway = discord.Embed(title="Giveaway", description=f"React with 🎉 to enter!\nPrize: {prize}\nTime remaining: {duration} seconds", color=discord.Color.from_rgb(0, 0, 0))
    embed_giveaway.set_image(url="https://cdn.discordapp.com/attachments/1234029947589365820/1234279370378444840/572424_10.png?ex=663027bd&is=662ed63d&hm=f2047257b023fdf85d1392b440bb0bfd5de17a8d75bad7d519c6c112a5d702fb&")
    message = await channel.send("@everyone", embed=embed_giveaway)
    await message.add_reaction("🎉")

    await asyncio.sleep(duration)

    message = await channel.fetch_message(message.id)
    reactions = message.reactions
    winner = None

    for reaction in reactions:
        if str(reaction.emoji) == "🎉":
            # Fetch the users who reacted with 🎉
            users = []
            async for user in reaction.users():
                users.append(user)
            # Filter out the bot user
            users = [user for user in users if user != ctx.bot.user]
            if users:
                # Choose a random winner from the remaining users
                winner = random.choice(users)
                break

    if winner:
        await channel.send(f"Congratulations {winner.mention}! You won the giveaway for {prize}!")
    else:
        await channel.send("No one participated in the giveaway. Better luck next time!")


@client.event
async def on_member_join(member):
    role_id = 1261510903204020374  # Replace this with your role ID
    role = member.guild.get_role(role_id)
    if role is not None:
        await member.add_roles(role)
        print(f"Added role {role.name} to {member.display_name}")

@client.command()
async def botinfo(ctx):
    creator_name = "agxmm"
    latency = round(client.latency * 1000)  # Using client instead of bot
    version = discord.__version__
    image_url = "https://media.discordapp.net/attachments/1267314338696396883/1267317855733416047/Untitled_design_4.png?ex=66a8593a&is=66a707ba&hm=48fd4e2fee0744b1853646555265e065314e844b83b9afb56a5a081888b57c68&=&format=webp&quality=lossless&width=550&height=309"

    embed = discord.Embed(title="Bot Information", color=discord.Color.from_rgb(0, 0, 0))  # Color set to #572424
    embed.add_field(name="Bot Ping", value=f"{latency}ms", inline=False)
    embed.add_field(name="Creator", value=creator_name, inline=False)
    embed.add_field(name="Discord.py Version", value=version, inline=False)
    embed.set_image(url=image_url)

    await ctx.send(embed=embed)


client.run(TOKEN)
