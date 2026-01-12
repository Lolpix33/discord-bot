import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import time
import random
from datetime import datetime, timedelta

# ==================== PATH DATI ====================
DATA_DIR = "data"
STAFF_FILE = os.path.join(DATA_DIR, "staff_hours.json")
PUNTI_FILE = os.path.join(DATA_DIR, "punti.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ==================== FUNZIONI JSON ====================
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

staff_data = load_json(STAFF_FILE, {})
punti_data = load_json(PUNTI_FILE, {})

# ==================== CONFIG ====================
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
MAIN_GUILD_ID = 1278033707457843314

# Ruoli
ADV_MOD_ROLE_ID = 1399839659961618513
SERVICE_ROLE_ID = 1450228259018113187
ORESTAFF_ROLE_ID = 1426308704759976108
DIRETTORE_ROLE_ID = 1426308704759976108
CEO_DIRETTORE_IDS = [1382481167894450319, DIRETTORE_ROLE_ID]

# Canali
STAFF_CHANNEL_ID = 1399142358116995173
SERVICE_CHANNEL_ID = 1450225638224171090
GENERAL_CHANNEL_ID = 1385409744444981389
PROMO_CHANNEL_ID = 1385409744444981389
STAFF_REMINDER_CHANNEL_ID = 1399142358116995173
PUNISH_LOG_CHANNEL_ID = STAFF_CHANNEL_ID

YOUTUBE_LINK = "https://www.youtube.com/@Ombra130"

# ==================== BOT ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ==================== CHECKS ====================
def owner_or_direttore_check():
    async def predicate(ctx):
        return ctx.author.id == ctx.guild.owner_id or any(r.id == DIRETTORE_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)

def dm_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(r.id == ADV_MOD_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)

def service_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(r.id == SERVICE_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)

def orestaff_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(r.id == ORESTAFF_ROLE_ID for r in ctx.author.roles)
    return commands.check(predicate)

def ceo_direttore_check():
    async def predicate(ctx):
        if ctx.author.id in CEO_DIRETTORE_IDS or ctx.author.guild_permissions.administrator:
            return True
        await ctx.send("❌ Non hai il permesso di usare questo comando.")
        return False
    return commands.check(predicate)

# ==================== UTILITY ====================
def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

def is_allowed_time():
    now = datetime.now().time()
    start_time = datetime.strptime("10:00", "%H:%M").time()
    end_time = datetime.strptime("01:00", "%H:%M").time()
    return start_time <= now or now <= end_time

def get_rank(hours):
    if hours >= 250*3600: return "🏆 Staff Unico"
    elif hours >= 100*3600: return "🥇 Staff Esperto"
    elif hours >= 60*3600: return "🥈 Staff Da esempio"
    elif hours >= 30*3600: return "🥉 Staff Avanzato"
    elif hours >= 10*3600: return "🎖 Staff Attivo"
    elif hours >= 5*3600: return "⭐ Staff Intraprendente"
    else: return "🔰 Nuovo Staff"

# ==================== SALVATAGGIO ====================
def save_staff():
    save_json(STAFF_FILE, staff_data)

def save_punti():
    save_json(PUNTI_FILE, punti_data)

# ==================== EMBED UTILITY ====================
def create_announcement_embed(testo):
    embed = discord.Embed(
        title="🚨 ANNUNCIO UFFICIALE 🚨",
        description=f"📣 **{testo}**",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Tutte le risposte al bot saranno visionate dallo staff di Ombra del 130 •")
    return embed

def punishment_embed(tipo, staff, motivo, durata=None):
    descrizione = f"👮 **Staff:** {staff}\n📌 **Motivo:** {motivo}\n"
    if durata: descrizione += f"⏳ **Durata:** {durata}\n"
    embed = discord.Embed(title=f"⚠️ {tipo.upper()} APPLICATO", description=descrizione, color=discord.Color.red(), timestamp=discord.utils.utcnow())
    embed.set_footer(text="Staff Ombra del 130 • Rispetta il regolamento")
    return embed

# ==================== ON READY ====================
@bot.event
async def on_ready():
    if MAIN_GUILD_ID not in [g.id for g in bot.guilds]:
        print("❌ Bot avviato in un server NON autorizzato")
        await bot.close()
        return
    print(f"🤖 {bot.user} ONLINE nel server autorizzato")
    if not promozione_youtube.is_running(): promozione_youtube.start()
    if not promemoria_staff.is_running(): promemoria_staff.start()
    if not vetrina_rank_staff.is_running(): vetrina_rank_staff.start()

# ==================== COMANDI STAFF ====================
@bot.command()
@service_check()
async def servizio(ctx, stato: str):
    uid = str(ctx.author.id)
    now = time.time()
    staff_data.setdefault(uid, {"totale":0,"inizio":None,"pausa":False,"messaggi":0,"comandi":0,"dm_gestiti":0,"vc_minuti":0})
    channel = bot.get_channel(SERVICE_CHANNEL_ID)

    if stato.lower() == "on":
        if staff_data[uid]["inizio"]: return await ctx.reply("⚠️ Sei già in servizio")
        staff_data[uid]["inizio"] = now
        save_staff()
        await channel.send(embed=discord.Embed(title="🟢 ENTRATA IN SERVIZIO", description=f"👮 {ctx.author.mention} è ora **IN SERVIZIO**", color=discord.Color.green(), timestamp=discord.utils.utcnow()))

    elif stato.lower() == "off":
        if not staff_data[uid]["inizio"]: return await ctx.reply("⚠️ Non sei in servizio")
        durata = now - staff_data[uid]["inizio"]
        staff_data[uid]["totale"] += durata
        staff_data[uid]["inizio"] = None
        save_staff()
        rank = get_rank(staff_data[uid]["totale"])
        embed = discord.Embed(title="🔴 USCITA DAL SERVIZIO", description=f"👮 {ctx.author.mention}\n⏱ Sessione: **{format_time(durata)}**\n🏅 Rank attuale: {rank}", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        await channel.send(embed=embed)

# ==================== DM & PUNIZIONI ====================
@bot.command()
@dm_check()
async def kick(ctx, member: discord.Member, *, motivo: str):
    try: await member.send(embed=punishment_embed("Kick", ctx.author.mention, motivo))
    except: pass
    await member.kick(reason=motivo)
    log = bot.get_channel(PUNISH_LOG_CHANNEL_ID)
    if log: await log.send(embed=punishment_embed("Kick", ctx.author.mention, motivo))
    await ctx.reply(f"👢 **{member} espulso correttamente**")

@bot.command()
@dm_check()
async def timeout(ctx, member: discord.Member, minuti: int, *, motivo: str):
    fine = discord.utils.utcnow() + timedelta(minutes=minuti)
    try: await member.send(embed=punishment_embed("Timeout", ctx.author.mention, motivo, f"{minuti} minuti"))
    except: pass
    await member.edit(timed_out_until=fine, reason=motivo)
    log = bot.get_channel(PUNISH_LOG_CHANNEL_ID)
    if log: await log.send(embed=punishment_embed("Timeout", ctx.author.mention, motivo, f"{minuti} minuti"))
    await ctx.reply(f"⏱ **Timeout applicato a {member} per {minuti} minuti**")

@bot.command()
@dm_check()
async def ban(ctx, member: discord.Member, *, motivo: str):
    try: await member.send(embed=punishment_embed("Ban", ctx.author.mention, motivo))
    except: pass
    await member.ban(reason=motivo, delete_message_days=1)
    log = bot.get_channel(PUNISH_LOG_CHANNEL_ID)
    if log: await log.send(embed=punishment_embed("Ban", ctx.author.mention, motivo))
    await ctx.reply(f"🔨 **{member} bannato permanentemente**")

# ==================== LOOP AUTOMATICI ====================
@tasks.loop(hours=3)
async def promozione_youtube():
    if not is_allowed_time(): return
    channel = bot.get_channel(PROMO_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="📢 Segui Ombra del 130 su YouTube!", description=f"➡️ [Clicca qui]({YOUTUBE_LINK})", color=discord.Color.gold(), timestamp=discord.utils.utcnow())
        embed.set_footer(text="💡 Non dimenticare di iscriverti e attivare la campanella!")
        await channel.send("💡 EHI NON DIMENTICARTI!", embed=embed)

@tasks.loop(minutes=120)
async def promemoria_staff():
    if not is_allowed_time(): return
    channel = bot.get_channel(STAFF_REMINDER_CHANNEL_ID)
    if not channel: return
    guild = bot.guilds[0]
    ruolo_staff = guild.get_role(SERVICE_ROLE_ID)
    in_servizio = [m.mention for m in ruolo_staff.members if staff_data.get(str(m.id), {}).get("inizio")]
    non_in_servizio = [m.mention for m in ruolo_staff.members if m.mention not in in_servizio]
    embed = discord.Embed(title="⏱ Stato Staff in Servizio", description=f"**In Servizio:** {' '.join(in_servizio) if in_servizio else 'Nessuno'}\n**Non in Servizio:** {' '.join(non_in_servizio) if non_in_servizio else 'Nessuno'}", color=discord.Color.blue(), timestamp=discord.utils.utcnow())
    embed.set_footer(text="💡 Ricorda di metterti in servizio se disponibile")
    await channel.send(f"{ruolo_staff.mention}", embed=embed)

# ==================== ON MESSAGE ====================
@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    if message.guild and uid in staff_data and staff_data[uid].get("inizio") and not staff_data[uid].get("pausa"):
        staff_data[uid]["messaggi"] += 1
        save_staff()
    if isinstance(message.channel, discord.DMChannel):
        staff_channel = bot.get_channel(STAFF_CHANNEL_ID)
        if staff_channel:
            embed = discord.Embed(title="📩 NUOVO MESSAGGIO AL BOT", color=discord.Color.dark_gold(), timestamp=discord.utils.utcnow())
            embed.add_field(name="👤 Utente", value=f"{message.author} (`{message.author.id}`)", inline=False)
            embed.add_field(name="💬 Messaggio", value=message.content or "*[Allegato o messaggio vuoto]*", inline=False)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="DM ricevuto • Staff Ombra del 130")
            await staff_channel.send(embed=embed)
        for staff_uid, dati in staff_data.items():
            if dati.get("inizio") and not dati.get("pausa"):
                dati["dm_gestiti"] += 1
                save_staff()
                break
        try:
            await message.author.send("✅ **Messaggio ricevuto!** Lo staff sta leggendo la tua richiesta.")
        except: pass
    await bot.process_commands(message)

# ==================== AVVIO BOT ====================
bot.run(TOKEN)
