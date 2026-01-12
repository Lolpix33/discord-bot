import discord
from discord.ext import commands, tasks
import json
import time
import random
from datetime import timedelta
from datetime import datetime
import os

# ================== PATH DATI ==================
DATA_DIR = "data"
STAFF_FILE = os.path.join(DATA_DIR, "staff_hours.json")
PUNTI_FILE = os.path.join(DATA_DIR, "punti.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ================== STAFF DATA ==================
if os.path.exists(STAFF_FILE):
    with open(STAFF_FILE, "r") as f:
        staff_data = json.load(f)
else:
    staff_data = {}

def save_staff():
    with open(STAFF_FILE, "w") as f:
        json.dump(staff_data, f, indent=4)

# ================== PUNTI DATA ==================
if os.path.exists(PUNTI_FILE):
    with open(PUNTI_FILE, "r") as f:
        punti_data = json.load(f)
else:
    punti_data = {}

def save_punti():
    with open(PUNTI_FILE, "w") as f:
        json.dump(punti_data, f, indent=4)

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

STAFF_FILE = os.path.join(DATA_DIR, "staff_hours.json")
PUNTI_FILE = os.path.join(DATA_DIR, "punti.json")

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)



ADV_MOD_ROLE_ID = 1399839659961618513   # Ruolo che può usare DM / DM RUOLO
SERVICE_ROLE_ID = 1450228259018113187   # Ruolo staff
ORESTAFF_ROLE_ID = 1426308704759976108 # Ruolo che può usare !orestaff
DIRETTORE_ROLE_ID = 1426308704759976108 # Ruolo Direttore (aggiunto)

# Ruoli che possono gestire i punti (Service + Addetto Punti + Direttore)
GESTORE_PUNTI_ROLE_IDS = [
    SERVICE_ROLE_ID,
    1454559530020245504,
    DIRETTORE_ROLE_ID
]

STAFF_CHANNEL_ID = 1399142358116995173  # Log DM
SERVICE_CHANNEL_ID = 1450225638224171090 # Log servizio
GENERAL_CHANNEL_ID = 1385409744444981389 # Generale per messaggi automatici
PROMO_CHANNEL_ID = 1385409744444981389  # Canale per messaggi YouTube
STAFF_REMINDER_CHANNEL_ID = 1399142358116995173 # Canale promemoria staff
PUNISH_LOG_CHANNEL_ID = STAFF_CHANNEL_ID  # usa il log staff che già hai


DATA_FILE = "staff_hours.json"
YOUTUBE_LINK = "https://www.youtube.com/@Ombra130"
# ==========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

MAIN_GUILD_ID = 1278033707457843314  # ID del tuo server

@bot.check
async def server_lock(ctx):
    if ctx.guild is None:
        return False
    return ctx.guild.id == MAIN_GUILD_ID


# ================= DATI =================


def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

def is_allowed_time():
    """
    Permette invio messaggi SOLO dalle 10:00 alle 01:00
    """
    now = datetime.now().time()
    start_time = datetime.strptime("10:00", "%H:%M").time()
    end_time = datetime.strptime("01:00", "%H:%M").time()

    # Intervallo che supera la mezzanotte
    if start_time <= now or now <= end_time:
        return True
    return False

# ================= RANK =================
def get_rank(hours):
    if hours >= 250*3600:
        return "🏆 Staff Unico"
    elif hours >= 100*3600:
        return "🥇 Staff Esperto"
    elif hours >= 60*3600:
        return "🥈 Staff Da esempio"
    elif hours >= 30*3600:
        return "🥉 Staff Avanzato"
    elif hours >= 10*3600:
        return "🎖 Staff Attivo"
    elif hours >= 5*3600:
        return "⭐ Staff Intraprendente"
    else:
        return "🔰 Nuovo Staff"

# ================= PERMESSI =================
DIRETTORE_ROLE_ID = 1426308704759976108

def owner_or_direttore_check():
    async def predicate(ctx):
        return (
            ctx.author.id == ctx.guild.owner_id or
            any(r.id == DIRETTORE_ROLE_ID for r in ctx.author.roles)
        )
    return commands.check(predicate)

def dm_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(
            r.id == ADV_MOD_ROLE_ID for r in ctx.author.roles
        )
    return commands.check(predicate)

def service_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(
            r.id == SERVICE_ROLE_ID for r in ctx.author.roles
        )
    return commands.check(predicate)

def founder_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def orestaff_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(
            r.id == ORESTAFF_ROLE_ID for r in ctx.author.roles
        )
    return commands.check(predicate)

# ================= ANNUNCI EMBED =================
def create_announcement_embed(ctx, testo):
    embed = discord.Embed(
        title="🚨 ANNUNCIO UFFICIALE 🚨",
        description=f"""
╔════════════════════════════╗

📣 **{testo}**

╚════════════════════════════╝
""",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(
        text="Tutte le risposte al bot saranno visionate dallo staff di Ombra del 130 •"
    )
    return embed

def punishment_embed(tipo, staff, motivo, durata=None):
    descrizione = (
        f"👮 **Staff:** {staff}\n"
        f"📌 **Motivo:** {motivo}\n"
    )

    if durata:
        descrizione += f"⏳ **Durata:** {durata}\n"

    embed = discord.Embed(
        title=f"⚠️ {tipo.upper()} APPLICATO",
        description=descrizione,
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Staff Ombra del 130 • Rispetta il regolamento")
    return embed

@bot.command()
@dm_check()
async def kick(ctx, member: discord.Member, *, motivo: str):
    try:
        await member.send(
            embed=punishment_embed(
                "Kick",
                ctx.author.mention,
                motivo
            )
        )
    except:
        pass

    await member.kick(reason=motivo)

    log = bot.get_channel(PUNISH_LOG_CHANNEL_ID)
    if log:
        await log.send(
            embed=punishment_embed(
                "Kick",
                ctx.author.mention,
                motivo
            )
        )

    await ctx.reply(f"👢 **{member} espulso correttamente**")

@bot.command()
@dm_check()
async def timeout(ctx, member: discord.Member, minuti: int, *, motivo: str):
    durata = timedelta(minutes=minuti)
    fine = discord.utils.utcnow() + durata

    try:
        await member.send(
            embed=punishment_embed(
                "Timeout",
                ctx.author.mention,
                motivo,
                f"{minuti} minuti"
            )
        )
    except:
        pass

    await member.edit(timed_out_until=fine, reason=motivo)

    log = bot.get_channel(PUNISH_LOG_CHANNEL_ID)
    if log:
        await log.send(
            embed=punishment_embed(
                "Timeout",
                ctx.author.mention,
                motivo,
                f"{minuti} minuti"
            )
        )

    await ctx.reply(f"⏱ **Timeout applicato a {member} per {minuti} minuti**")

@bot.command()
@dm_check()
async def ban(ctx, member: discord.Member, *, motivo: str):
    try:
        await member.send(
            embed=punishment_embed(
                "Ban",
                ctx.author.mention,
                motivo
            )
        )
    except:
        pass

    await member.ban(reason=motivo, delete_message_days=1)

    log = bot.get_channel(PUNISH_LOG_CHANNEL_ID)
    if log:
        await log.send(
            embed=punishment_embed(
                "Ban",
                ctx.author.mention,
                motivo
            )
        )

    await ctx.reply(f"🔨 **{member} bannato permanentemente**")

def create_buttons():
    view = discord.ui.View(timeout=None)
    view.add_item(
        discord.ui.Button(
            label="🔗 Entra nel server",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/dWcNW5EuyA"
        )
    )
    view.add_item(
        discord.ui.Button(
            label="📩 Contatta lo staff",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/n5n3DnvU4V"
        )
    )
    return view

# ================= DM SINGOLO =================
@bot.command()
@dm_check()
async def dm(ctx, user: discord.User, *, testo):
    if user.bot:
        return await ctx.reply("❌ Non puoi inviare DM a un bot.")
    embed = create_announcement_embed(ctx, testo)
    view = create_buttons()
    try:
        await user.send(embed=embed, view=view)
        await ctx.reply(f"✅ Annuncio inviato a {user.mention}")
    except:
        await ctx.reply("❌ DM non inviabile")

# ================= DM RUOLO =================
@bot.command()
@dm_check()
async def dmruolo(ctx, ruolo: discord.Role, *, testo):
    embed = create_announcement_embed(ctx, testo)
    view = create_buttons()
    inviati = 0
    falliti = 0
    for membro in ruolo.members:
        if membro.bot:
            continue
        try:
            await membro.send(embed=embed, view=view)
            inviati += 1
        except:
            falliti += 1
    await ctx.reply(
        f"📨 **DM RUOLO COMPLETATO**\n✅ Inviati: **{inviati}**\n❌ Falliti: **{falliti}**"
    )

# ================= SERVIZIO =================
@bot.command()
@service_check()
async def servizio(ctx, stato: str):
    uid = str(ctx.author.id)
    now = time.time()
    staff_data.setdefault(uid, {
    "totale": 0,
    "inizio": None,
    "pausa": False,
    "messaggi": 0,
    "comandi": 0,
    "dm_gestiti": 0,
    "vc_minuti": 0
})

    channel = bot.get_channel(SERVICE_CHANNEL_ID)

    if stato.lower() == "on":
        if staff_data[uid]["inizio"]:
            return await ctx.reply("⚠️ Sei già in servizio")
        staff_data[uid]["inizio"] = now
        save_staff()
        embed = discord.Embed(
            title="🟢 ENTRATA IN SERVIZIO",
            description=f"👮 {ctx.author.mention} è ora **IN SERVIZIO**",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=embed)

    elif stato.lower() == "off":
        if not staff_data[uid]["inizio"]:
            return await ctx.reply("⚠️ Non sei in servizio")
        durata = now - staff_data[uid]["inizio"]
        staff_data[uid]["totale"] += durata
        staff_data[uid]["inizio"] = None
        save_staff()

        rank = get_rank(staff_data[uid]["totale"])
        embed = discord.Embed(
            title="🔴 USCITA DAL SERVIZIO",
            description=(
                f"👮 {ctx.author.mention}\n"
                f"⏱ Sessione: **{format_time(durata)}**\n"
                f"🏅 Rank attuale: {rank}"
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=embed)
    else:
        await ctx.reply("❌ NON ESISTE QUESTO COMANDO | DEVI USARE IL PANNELLO IN SERVIZIO STAFF E CLICCARE ENTRA IN SERVIZIO")

# ================= SERVIZIO CON BOTTONI =================
class ServizioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🟢 Mettiti in Servizio", style=discord.ButtonStyle.success)
    async def servizio_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        now = time.time()

        staff_data.setdefault(uid, {
    "totale": 0,
    "inizio": None,
    "pausa": False,
    "messaggi": 0,
    "comandi": 0,
    "dm_gestiti": 0,
    "vc_minuti": 0
})


        if staff_data[uid]["inizio"] and not staff_data[uid].get("pausa"):
            return await interaction.response.send_message(
                "⚠️ Sei già in servizio", ephemeral=True
            )

        staff_data[uid]["inizio"] = now
        staff_data[uid]["pausa"] = False
        save_staff()


        await interaction.response.send_message(
            "🟢 **Sei ora IN SERVIZIO**", ephemeral=True
        )

    @discord.ui.button(label="🟡 Pausa Servizio", style=discord.ButtonStyle.secondary)
    async def servizio_pausa(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)

        if uid not in staff_data or (not staff_data[uid]["inizio"] and not staff_data[uid].get("pausa")):
            return await interaction.response.send_message(
                "⚠️ Non sei in servizio", ephemeral=True
            )

        if staff_data[uid].get("pausa"):
            # Riprendi servizio
            staff_data[uid]["pausa"] = False
            staff_data[uid]["inizio"] = time.time()
            save_staff()

            button.label = "🟡 Pausa Servizio"  # Cambia label bottone
            await interaction.response.edit_message(view=self)  # Aggiorna la view
            await interaction.followup.send("🟢 **Hai ripreso il servizio**", ephemeral=True)

        else:
            # Metti in pausa
            durata = time.time() - staff_data[uid]["inizio"]
            staff_data[uid]["totale"] += durata
            staff_data[uid]["pausa"] = True
            staff_data[uid]["inizio"] = None
            save_staff()

            button.label = "🟢 Riprendi Servizio"  # Cambia label bottone
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("🟡 **Servizio messo in PAUSA**", ephemeral=True)

    @discord.ui.button(label="🔴 Esci dal Servizio", style=discord.ButtonStyle.danger)
    async def servizio_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        now = time.time()
        DIRETTORE_ROLE_ID = 1426308704759976108

        if uid not in staff_data or not staff_data[uid]["inizio"]:
            if staff_data.get(uid, {}).get("pausa"):
                durata = 0
            else:
                return await interaction.response.send_message(
                    "⚠️ Non sei in servizio", ephemeral=True
                )
        else:
            durata = now - staff_data[uid]["inizio"] if not staff_data[uid].get("pausa") else 0
            staff_data[uid]["totale"] += durata

        staff_data[uid]["inizio"] = None
        staff_data[uid]["pausa"] = False
        save_staff()


        rank = get_rank(staff_data[uid]["totale"])

        embed_owner = discord.Embed(
            title=f"🔴 {interaction.user.display_name} è uscito dal servizio",
            description=(
                f"👮 Staff: {interaction.user.mention}\n"
                f"⏱ Durata sessione: **{format_time(durata)}**\n"
                f"⏱ Ore totali: **{format_time(staff_data[uid]['totale'])}**\n"
                f"🏅 Rank attuale: {rank}"
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        try:
            await interaction.guild.owner.send(embed=embed_owner)
        except:
            pass

        direttore_role = interaction.guild.get_role(DIRETTORE_ROLE_ID)
        if direttore_role:
            for membro in direttore_role.members:
                try:
                    await membro.send(embed=embed_owner)
                except:
                    pass

        await interaction.response.send_message(
            f"🔴 Sei uscito dal servizio!\n⏱ Durata sessione: **{format_time(durata)}**\n⏱ Ore totali: **{format_time(staff_data[uid]['totale'])}**\n🏅 Rank attuale: {rank}",
            ephemeral=True
        )





@bot.command()
@service_check()
async def pannelloservizio(ctx):
    embed = discord.Embed(
        title="🛡️ PANNELLO SERVIZIO STAFF",
        description=(
            "Usa i **bottoni qui sotto** per gestire il tuo servizio:\n\n"
            "🟢 **IN SERVIZIO** → Inizia a contare le ore\n"
            "🟡 **PAUSA** → Ferma temporaneamente il conteggio\n"
            "🔴 **OFF** → Termina il servizio"
        ),
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=ServizioView())


# ================= COMANDI FOUNDER =================
@bot.command()
@owner_or_direttore_check()
async def aggiungiore(ctx, member: discord.Member, ore: float):
    uid = str(member.id)
    staff_data.setdefault(uid, {
    "totale": 0,
    "inizio": None,
    "pausa": False,
    "messaggi": 0,
    "comandi": 0,
    "dm_gestiti": 0,
    "vc_minuti": 0
})

    staff_data[uid]["totale"] += ore * 3600
    save_staff()

    await ctx.send(f"✅ Aggiunte {ore} ore a {member.mention}")

@bot.command()
@owner_or_direttore_check()
async def togliore(ctx, member: discord.Member, ore: float):
    uid = str(member.id)
    if uid not in staff_data:
        return await ctx.send("❌ Nessun dato trovato")
    staff_data[uid]["totale"] = max(
        0, staff_data[uid]["totale"] - ore * 3600
    )
    save_staff()

    await ctx.send(f"⛔ Tolte {ore} ore a {member.mention}")

# ================= RANK E ORE STAFF =================
@bot.command()
@orestaff_check()
async def orestaff(ctx, member: discord.Member):
    uid = str(member.id)
    if uid not in staff_data:
        return await ctx.send("❌ Nessun dato trovato")
    totale = staff_data[uid]["totale"]
    rank = get_rank(totale)
    embed = discord.Embed(
        title=f"📊 Ore e Rank di {member}",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="⏱ Ore Totali",
        value=format_time(totale),
        inline=False
    )
    embed.add_field(
        name="🏅 Rank",
        value=rank,
        inline=False
    )
    await ctx.send(embed=embed)


# ================= REPORT STAFF GRAFICO EVOLUTO =================
@bot.command()
@owner_or_direttore_check()
async def reportstaffgrafico(ctx):
    guild = ctx.guild
    ruolo_staff = guild.get_role(SERVICE_ROLE_ID)
    if not ruolo_staff:
        return await ctx.send("❌ Ruolo staff non trovato")

    # Definizione step ore per rank
    rank_steps = [
        (0, "🔰 Nuovo Staff"),
        (5*3600, "⭐ Staff Intraprendente"),
        (10*3600, "🎖 Staff Attivo"),
        (30*3600, "🥉 Staff Avanzato"),
        (60*3600, "🥈 Staff Da esempio"),
        (100*3600, "🥇 Staff Esperto"),
        (250*3600, "🏆 Staff Unico")
    ]

    embed = discord.Embed(
        title="📊 Report Staff Ombra del 130",
        description="Ecco le ore e i rank di tutto lo staff con progresso verso il prossimo rank!",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    )

    for membro in ruolo_staff.members:
        uid = str(membro.id)
        totale = staff_data.get(uid, {}).get("totale", 0)

        # Trova rank attuale e prossimo
        current_rank = rank_steps[0][1]
        next_rank_hours = None
        for i, (ore, nome) in enumerate(rank_steps):
            if totale >= ore:
                current_rank = nome
                if i+1 < len(rank_steps):
                    next_rank_hours = rank_steps[i+1][0]
                else:
                    next_rank_hours = ore  # massimo raggiunto

        # Calcolo progresso verso il prossimo rank
        if next_rank_hours and next_rank_hours != totale:
            progress = totale / next_rank_hours
        else:
            progress = 1

        bar_total = 20
        filled = int(progress * bar_total)
        empty = bar_total - filled
        barra = "🟦" * filled + "⬜" * empty

        # Ore mancanti al prossimo rank
        ore_mancanti = max(0, next_rank_hours - totale) if next_rank_hours != totale else 0

        embed.add_field(
            name=f"👤 {membro.display_name}",
            value=(
                f"🏅 Rank attuale: **{current_rank}**\n"
                f"⏱ Ore totali: **{format_time(totale)}**\n"
                f"{barra}\n"
                f"⏳ Ore al prossimo rank: **{format_time(ore_mancanti)}**"
            ),
            inline=False
        )

    embed.set_footer(text="💡 Comando eseguibile solo da Owner o Direttore, ma visibile a tutti")
    await ctx.send(embed=embed)

    # -------------------- CLASSIFICA NEL CANALE GENERALE -------------------------------
@bot.command()
@owner_or_direttore_check()
async def classifica(ctx):
    """Mostra i top staff nel canale generale"""
    channel = bot.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return await ctx.send("❌ Canale generale non trovato")

    ruolo_staff = ctx.guild.get_role(SERVICE_ROLE_ID)
    if not ruolo_staff:
        return await ctx.send("❌ Ruolo staff non trovato")

    # Ordina i membri per ore totali
    staff_sorted = sorted(
        ruolo_staff.members,
        key=lambda m: staff_data.get(str(m.id), {}).get("totale", 0),
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 CLASSIFICA TOP STAFF – OMBRA DEL 130",
        description="🔥 I membri dello staff più attivi!",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    for i, membro in enumerate(staff_sorted[:10], start=1):
        totale = staff_data.get(str(membro.id), {}).get("totale", 0)
        rank = get_rank(totale)
        embed.add_field(
            name=f"#{i} • {membro.display_name}",
            value=f"{rank}\n⏱ **{format_time(totale)}**",
            inline=False
        )

    await channel.send(embed=embed)
    await ctx.reply(f"✅ Classifica inviata in {channel.mention}", ephemeral=True)  


# ================= LOOP AUTOMATICI =================
@tasks.loop(hours=3)
async def promozione_youtube():
    if not is_allowed_time():
        return
    channel = bot.get_channel(PROMO_CHANNEL_ID)
    if not channel:
        return
    embed = discord.Embed(
        title="📢 Segui Ombra del 130 su YouTube!",
        description=f"➡️ [Clicca qui per il canale]({YOUTUBE_LINK})",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(
        text="💡 Non dimenticare di iscriverti e attivare la campanella!"
    )
    await channel.send("💡 EHI NON DIMENTICARTI!", embed=embed)

@tasks.loop(minutes=120)
async def promemoria_staff():
    if not is_allowed_time():
        return
    channel = bot.get_channel(STAFF_REMINDER_CHANNEL_ID)
    if not channel:
        return

    guild = bot.guilds[0]
    ruolo_staff = guild.get_role(SERVICE_ROLE_ID)

    in_servizio = []
    non_in_servizio = []

    for membro in ruolo_staff.members:
        uid = str(membro.id)
        if uid in staff_data and staff_data[uid].get("inizio"):
            in_servizio.append(membro.mention)
        else:
            non_in_servizio.append(membro.mention)

    embed = discord.Embed(
        title="⏱ Stato Staff in Servizio",
        description=(
            f"**In Servizio:** {' '.join(in_servizio) if in_servizio else 'Nessuno'}\n\n"
            f"**Non in Servizio:** {' '.join(non_in_servizio) if non_in_servizio else 'Nessuno'}"
        ),
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(
        text="💡 Ricorda di metterti in servizio se disponibile e per raggiungere le ore minime settimanali"
    )
    await channel.send(f"{ruolo_staff.mention}", embed=embed)

@tasks.loop(minutes=210)  # 3 ore e mezza
async def vetrina_rank_staff():
    channel = bot.get_channel(PROMO_CHANNEL_ID)
    if not channel:
        return

    guild = bot.guilds[0]
    ruolo_staff = guild.get_role(SERVICE_ROLE_ID)
    if not ruolo_staff:
        return

    embed = discord.Embed(
        title="🏆 CLASSIFICA STAFF – OMBRA DEL 130",
        description="🔥 Gli staff più attivi del server",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    staff_sorted = sorted(
        ruolo_staff.members,
        key=lambda m: staff_data.get(str(m.id), {}).get("totale", 0),
        reverse=True
    )

    for i, membro in enumerate(staff_sorted[:10], start=1):
        totale = staff_data.get(str(membro.id), {}).get("totale", 0)
        rank = get_rank(totale)

        embed.add_field(
            name=f"#{i} • {membro.display_name}",
            value=f"{rank}\n⏱ **{format_time(totale)}**",
            inline=False
        )

    embed.set_footer(text="💎 Diventa uno degli staff più attivi!")
    await channel.send(embed=embed)

# ================= ON READY =================

@bot.event
async def on_ready():
    guild_ids = [g.id for g in bot.guilds]

    if MAIN_GUILD_ID not in guild_ids:
        print("❌ Bot avviato in un server NON autorizzato")
        await bot.close()
        return

    print(f"🤖 {bot.user} ONLINE nel server autorizzato")

    # Avvio loop solo se non già partiti
    if not promozione_youtube.is_running():
        promozione_youtube.start()

    if not promemoria_staff.is_running():
        promemoria_staff.start()

    if not vetrina_rank_staff.is_running():
        vetrina_rank_staff.start()


@bot.event
async def on_message(message):
    # Ignora i messaggi del bot
    if message.author.bot:
        return

    uid = str(message.author.id)

    # ================= MESSAGGI IN SERVER (conteggio staff) =================
    if message.guild:
        if uid in staff_data:
            if staff_data[uid].get("inizio") and not staff_data[uid].get("pausa"):
                staff_data[uid]["messaggi"] += 1
                save_staff()

    # ================= MESSAGGI IN DM =================
    if isinstance(message.channel, discord.DMChannel):
        staff_channel = bot.get_channel(STAFF_CHANNEL_ID)

        # Log DM allo staff
        if staff_channel:
            embed = discord.Embed(
                title="📩 NUOVO MESSAGGIO AL BOT",
                color=discord.Color.dark_gold(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(
                name="👤 Utente",
                value=f"{message.author} (`{message.author.id}`)",
                inline=False
            )
            embed.add_field(
                name="💬 Messaggio",
                value=message.content or "*[Allegato o messaggio vuoto]*",
                inline=False
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="DM ricevuto • Staff Ombra del 130")

            await staff_channel.send(embed=embed)

        # ================= CONTA DM GESTITO =================
        for staff_uid, dati in staff_data.items():
            if dati.get("inizio") and not dati.get("pausa"):
                dati["dm_gestiti"] += 1
                save_staff()
                break  # solo UNO staff prende il DM

        # ================= RISPOSTA AUTOMATICA =================
        try:
            await message.author.send(
                "✅ **Messaggio ricevuto!**\n\n"
                "👀 Lo staff sta leggendo la tua richiesta.\n"
                "⏳ Ti risponderemo il prima possibile."
            )
        except:
            pass

    # FONDAMENTALE per far funzionare i comandi
    await bot.process_commands(message)



import asyncio

# ================= GESTIONE BOT =================
PUNTI_FILE = "punti.json"

# ================= GESTIONE PUNTI =================
GESTORE_PUNTI_ROLE_IDS = [SERVICE_ROLE_ID, 1454559530020245504]  # Tu + addetto punti

try:
    with open(PUNTI_FILE, "r") as f:
        punti_data = json.load(f)
except FileNotFoundError:
    punti_data = {}

def save_punti():
    with open(PUNTI_FILE, "w") as f:
        json.dump(punti_data, f, indent=4)

def punti_check():
    async def predicate(ctx):
        return any(r.id in GESTORE_PUNTI_ROLE_IDS for r in ctx.author.roles) or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def ceo_direttore_check():
    async def predicate(ctx):
        allowed_ids = [1382481167894450319,1426308704759976108]  # Inserisci ID CEO e Direttore
        if ctx.author.id in allowed_ids:
            return True
        await ctx.send("❌ Non hai il permesso di usare questo comando.")
        return False
    return commands.check(predicate)

# ================= LISTA PREMI =================
premi_list = [
    "🏆 Premio Leggendario",
    "🎖 Premio Epico",
    "🎉 Premio Raro",
    "💎 50 punti",
    "💎 100 punti",
    "🔥 Emoji Epica",
    "😎 Emoji Rara",
    "⭐ Boost punti x2",
    "🍀 Jackpot casuale",
    "🎰 Slot speciale"
]

# ================= COG GIOCO =================
class Gioco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_games = {}

    # ================= COMANDI CEO/DIRETTORE =================
    @commands.command()
    @ceo_direttore_check()
    async def aggiungipunti(self, ctx, member: discord.Member, punti: int):
        uid = str(member.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0, "badge": [], "livello": 1})
        punti_data[uid]["punti"] += punti
        save_punti()
        await ctx.send(f"✅ Aggiunti {punti} punti a {member.mention}. Totale: {punti_data[uid]['punti']}")

    @commands.command()
    @ceo_direttore_check()
    async def togli_punti(self, ctx, member: discord.Member, punti: int):
        uid = str(member.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0, "badge": [], "livello": 1})
        punti_data[uid]["punti"] = max(0, punti_data[uid]["punti"] - punti)
        save_punti()
        await ctx.send(f"⛔ Tolti {punti} punti a {member.mention}. Totale: {punti_data[uid]['punti']}")

    @commands.command()
    @ceo_direttore_check()
    async def salvapunti(self, ctx):
        save_punti()
        await ctx.send("💾 Tutti i punti sono stati salvati correttamente!")

    # ================= MENU PRINCIPALE =================
    @commands.command()
    async def menu(self, ctx):
        """Mostra il menu principale del gioco"""
        view = MainMenu(ctx)
        embed = discord.Embed(
            title="🎮 GIOCHI DI OMBRA DEL 130!",
            description="MODALITÀ INNOVATIVA DI GIOCARE PROVA ORA ANCHE TU I NUOVI MINIGIOCHI!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=view)

    # ================= MINIGIOCO CORSA =================
    @commands.command()
    async def corsa(self, ctx):
        """Minigioco: corri verso il traguardo"""
        uid = str(ctx.author.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0, "badge": [], "livello": 1})
        self.current_games[uid] = {"posizione": 0, "traguardo": 5}

        from discord.ui import Button, View

        async def muovi(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Questo non è il tuo gioco!", ephemeral=True)
                return
            game = self.current_games[uid]
            game["posizione"] += 1
            pos = game["posizione"]
            traguardo = game["traguardo"]
            if pos >= traguardo:
                punti_guadagnati = random.randint(20, 100)
                punti_data[uid]["punti"] += punti_guadagnati
                save_punti()
                del self.current_games[uid]
                await interaction.response.send_message(
                    content=f"🎉 Hai raggiunto il traguardo! Punti guadagnati: {punti_guadagnati}",
                    view=None
                )

            else:
                barra = "🏃" + "—" * pos + "🏁" + "—" * (traguardo-pos)
                await interaction.response.send_message(content=f"**Corsa:** {barra}", view=view)


        button = Button(label="Muovi", style=discord.ButtonStyle.green)
        button.callback = muovi
        view = View()
        view.add_item(button)
        barra_iniziale = "🏃" + "—" * 0 + "🏁" + "—" * 5
        await ctx.send(f"**Corsa:** {barra_iniziale}", view=view)


# ================= MENU DISCORD UI =================
class MainMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="🎲 Giochi casuali", style=discord.ButtonStyle.green)
    async def casual_games(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎲 Giochi casuali",
            description="1️⃣ Tiro dadi\n2️⃣ Indovina il numero\n3️⃣ Memoria\n4️⃣ Slot machine\n5️⃣ Quiz interattivo",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=CasualGamesMenu(self.ctx))


    @discord.ui.button(label="🏆 Classifica", style=discord.ButtonStyle.blurple)
    async def leaderboard(self, button: discord.ui.Button, interaction: discord.Interaction):
        sorted_users = sorted(punti_data.items(), key=lambda x: x[1]["punti"], reverse=True)
        descrizione = "\n".join([f"{i+1}. <@{uid}> - {data['punti']} punti" for i, (uid, data) in enumerate(sorted_users[:10])])
        embed = discord.Embed(title="🏆 Leaderboard Top 10", description=descrizione, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed, view=self)


    @discord.ui.button(label="🎁 Premi & Loot Box", style=discord.ButtonStyle.blurple)
    async def lootbox(self, button: discord.ui.Button, interaction: discord.Interaction):
        premio = random.choice(premi_list)
        embed = discord.Embed(
            title="🎁 Loot Box",
            description=f"Hai ricevuto: {premio}",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, view=self)


    @discord.ui.button(label="📊 Statistiche", style=discord.ButtonStyle.gray)
    async def stats(self, button: discord.ui.Button, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        punti = punti_data.get(uid, {}).get("punti", 0)
        giochi = punti_data.get(uid, {}).get("giochi", 0)
        embed = discord.Embed(
            title=f"📊 Statistiche di {interaction.user.display_name}",
            description=f"💎 Punti totali: {punti}\n🎲 Giochi giocati: {giochi}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=self)



class CasualGamesMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    # -------- TIRO DADI --------
    @discord.ui.button(label="🎲 Tiro Dadi", style=discord.ButtonStyle.primary)
    async def dice_game(self, button: discord.ui.Button, interaction: discord.Interaction):
        dado1 = random.randint(1,6)
        dado2 = random.randint(1,6)
        totale = dado1 + dado2
        uid = str(interaction.user.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0})
        punti_data[uid]["punti"] += totale
        punti_data[uid]["giochi"] += 1
        save_punti()
        embed = discord.Embed(title="🎲 Tiro Dadi",
                              description=f"Hai tirato: {dado1} + {dado2} = {totale}\nTotale punti: {punti_data[uid]['punti']}",
                              color=discord.Color.green())
        await (embed=embed, view=self)

    # -------- INDOVINA IL NUMERO --------
    @discord.ui.button(label="🔢 Indovina il numero", style=discord.ButtonStyle.primary)
    async def guess_number(self, button: discord.ui.Button, interaction: discord.Interaction):
        numero = random.randint(1,20)
        uid = str(interaction.user.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0})
        punti_data[uid]["giochi"] += 1

        await interaction.response.send_message("Indovina un numero tra 1 e 20 usando la chat!", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id and m.content.isdigit()

        try:
            msg = await bot.wait_for("message", check=check, timeout=15)
            guess = int(msg.content)
            if guess == numero:
                punti_data[uid]["punti"] += 50
                result_msg = "🎉 Esatto! +50 punti!"
            elif abs(guess-numero) <= 2:
                punti_data[uid]["punti"] += 20
                result_msg = f"✅ Quasi! Il numero era {numero}. +20 punti!"
            else:
                result_msg = f"❌ Sbagliato! Il numero era {numero}."
            save_punti()
            await interaction.followup.send(result_msg)
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⏰ Tempo scaduto! Il numero era {numero}.")

    # -------- MEMORY --------
    @discord.ui.button(label="🧠 Memory", style=discord.ButtonStyle.primary)
    async def memory_game(self, button: discord.ui.Button, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0})
        punti_data[uid]["giochi"] += 1
        # Creazione griglia memory con emoji
        emoji_list = ["🍎","🍌","🍒","🍇","🍉","🍋"]*2
        random.shuffle(emoji_list)
        board = [emoji_list[i:i+4] for i in range(0, len(emoji_list),4)]
        display_board = "\n".join([" ".join(row) for row in board])
        punti_data[uid]["punti"] += 30
        save_punti()
        await interaction.response.send_message(f"🧠 Memory Game: Ottimo lavoro! +30 punti\n{display_board}", ephemeral=True)

    # -------- SLOT MACHINE --------
    @discord.ui.button(label="🎰 Slot Machine", style=discord.ButtonStyle.primary)
    async def slot_machine(self, button: discord.ui.Button, interaction: discord.Interaction):
        emojis = ["🍒", "🍋", "🍉", "⭐", "🔔", "💎", "🍀"]
        risultato = [random.choice(emojis) for _ in range(3)]
        uid = str(interaction.user.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0})
        punti_data[uid]["giochi"] += 1
        punti_data[uid]["punti"] -= 10  # costo di gioco

        # Verifica vincita
        if len(set(risultato)) == 1:
            vincita = random.randint(50, 150)
            punti_data[uid]["punti"] += vincita
            msg = f"🎉 JACKPOT! Hai vinto {vincita} punti!\n{' | '.join(risultato)}"
        elif len(set(risultato)) == 2:
            vincita = random.randint(10, 30)
            punti_data[uid]["punti"] += vincita
            msg = f"✅ Piccola vincita! Hai guadagnato {vincita} punti\n{' | '.join(risultato)}"
        else:
            msg = f"❌ Peccato! Non hai vinto punti\n{' | '.join(risultato)}"

        save_punti()
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=msg + f"\n💎 Punti totali: {punti_data[uid]['punti']}",
            color=discord.Color.purple()
        )
        await (embed=embed, view=self)


    # -------- QUIZ --------
    @discord.ui.button(label="❓ Quiz", style=discord.ButtonStyle.primary)
    async def quiz_game(self, button: discord.ui.Button, interaction: discord.Interaction):
        quiz_list = [
            {"domanda": "Qual è la capitale d'Italia?", "risposta": "roma"},
            {"domanda": "Qual è il colore del cielo?", "risposta": "azzurro"},
            {"domanda": "Chi ha scritto 'La Divina Commedia'?", "risposta": "dante"},
            {"domanda": "Qual è la capitale della Francia?", "risposta": "parigi"},
            {"domanda": "Che animale è considerato il re della savana?", "risposta": "leone"},
            {"domanda": "Quanti continenti ci sono sulla Terra?", "risposta": "7"},
            {"domanda": "Qual è la capitale dell'Italia?", "risposta": "roma"},
            {"domanda": "Qual è il fiume più lungo del mondo?", "risposta": "nilo"},
            {"domanda": "Chi ha scritto 'La Divina Commedia'?", "risposta": "dante"},
            {"domanda": "Qual è il colore del cielo?", "risposta": "azzurro"},
            {"domanda": "Quanti giorni ci sono in una settimana?", "risposta": "7"},
            {"domanda": "Qual è il più grande mammifero terrestre?", "risposta": "elefante"},
            {"domanda": "Qual è la capitale della Francia?", "risposta": "parigi"},
            {"domanda": "Chi ha dipinto la Gioconda?", "risposta": "da vinci"},
            {"domanda": "Quale animale è conosciuto come il re della savana?", "risposta": "leone"},
            {"domanda": "Quanti continenti ci sono sulla Terra?", "risposta": "7"},
            {"domanda": "Qual è il pianeta più vicino al Sole?", "risposta": "mercurio"},
            {"domanda": "Qual è il numero di mesi in un anno?", "risposta": "12"},
            {"domanda": "Qual è la moneta ufficiale del Giappone?", "risposta": "yen"},
            {"domanda": "Chi ha scoperto l'America?", "risposta": "cristoforo colombo"},
            {"domanda": "Qual è la capitale della Germania?", "risposta": "berlino"},
            {"domanda": "Quale animale produce il miele?", "risposta": "ape"},
            {"domanda": "Che gas respiriamo principalmente?", "risposta": "ossigeno"},
            {"domanda": "Qual è la lingua più parlata al mondo?", "risposta": "cinese"},
            {"domanda": "Chi ha scritto 'I promessi sposi'?", "risposta": "manzoni"},
            {"domanda": "Che strumento misura la temperatura?", "risposta": "termometro"},
            {"domanda": "Quante stagioni ci sono in un anno?", "risposta": "4"},
            {"domanda": "Qual è la capitale della Spagna?", "risposta": "madrid"},
            {"domanda": "Chi ha inventato il telefono?", "risposta": "bell"},
            {"domanda": "Qual è il numero atomico dell'ossigeno?", "risposta": "8"},
            {"domanda": "Che animale ha le strisce bianche e nere?", "risposta": "zebra"},
            {"domanda": "Qual è la montagna più alta del mondo?", "risposta": "everest"},
            {"domanda": "Qual è il pianeta più grande del sistema solare?", "risposta": "giove"},
            {"domanda": "Che numero viene dopo 99?", "risposta": "100"},
            {"domanda": "Qual è la valuta ufficiale degli Stati Uniti?", "risposta": "dollaro"},
            {"domanda": "Chi ha scritto 'Romeo e Giulietta'?", "risposta": "shakespeare"},
            {"domanda": "Qual è il colore del latte?", "risposta": "bianco"},
            {"domanda": "Che forma ha la Terra?", "risposta": "sfera"},
            {"domanda": "Quanti denti ha un adulto?", "risposta": "32"},
            {"domanda": "Qual è l’animale simbolo della Cina?", "risposta": "panda"},
            {"domanda": "Che animale vive nel polo nord?", "risposta": "orso polare"},
            {"domanda": "Chi ha inventato la lampadina?", "risposta": "edison"},
            {"domanda": "Qual è la capitale della Turchia?", "risposta": "ankara"},
            {"domanda": "Qual è il colore della bandiera italiana?", "risposta": "verde bianco rosso"},
            {"domanda": "Che numero viene prima del 50?", "risposta": "49"},
            {"domanda": "Quanti minuti ci sono in un'ora?", "risposta": "60"},
            {"domanda": "Chi ha inventato il computer?", "risposta": "turing"},
            {"domanda": "Qual è il più grande oceano del mondo?", "risposta": "oceano pacifico"},
            {"domanda": "Qual è l'animale più grande del mondo?", "risposta": "balena"},
            {"domanda": "Quale lingua si parla in Brasile?", "risposta": "portoghese"},
            {"domanda": "Che animale ha il collo più lungo?", "risposta": "giraffa"},
            {"domanda": "Che animale ha il corno sul naso?", "risposta": "rinoceronte"},
            {"domanda": "Quanti oceani ci sono sulla Terra?", "risposta": "5"},
            {"domanda": "Qual è il simbolo chimico dell'oro?", "risposta": "au"},
            {"domanda": "Qual è la capitale del Messico?", "risposta": "città del messico"},
            {"domanda": "Quanti giorni ha febbraio negli anni bisestili?", "risposta": "29"},
            {"domanda": "Chi ha scritto 'Iliade'?", "risposta": "omero"},
            {"domanda": "Qual è il simbolo chimico del carbonio?", "risposta": "c"},
            {"domanda": "Chi ha inventato il telegrafo?", "risposta": "morse"},
            {"domanda": "Qual è la capitale della Norvegia?", "risposta": "oslo"},
            {"domanda": "Che numero viene dopo 19?", "risposta": "20"}
        ]
        quiz = random.choice(quiz_list)
        uid = str(interaction.user.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0})
        punti_data[uid]["giochi"] += 1

        await interaction.response.send_message(f"❓ **Quiz:** {quiz['domanda']}", ephemeral=True)
        def check(m):
            return m.author.id == interaction.user.id

        try:
            msg = await bot.wait_for("message", check=check, timeout=20)
            if msg.content.lower().strip() == quiz["risposta"]:
                punti_data[uid]["punti"] += 50
                save_punti()
                await interaction.followup.send("✅ Risposta corretta! +50 punti")
            else:
                await interaction.followup.send(f"❌ Risposta sbagliata! La risposta era: {quiz['risposta']}")
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⏰ Tempo scaduto! La risposta era: {quiz['risposta']}")

    # -------- CORSA --------
    @discord.ui.button(label="🏃 Corsa", style=discord.ButtonStyle.primary)
    async def corsa_game(self, button: discord.ui.Button, interaction: discord.Interaction):
        from discord.ui import Button, View
        uid = str(interaction.user.id)
        punti_data.setdefault(uid, {"punti": 0, "giochi": 0, "badge": [], "livello": 1})
        punti_data[uid]["giochi"] += 1

        current_games = {uid: {"posizione": 0, "traguardo": 5}}

    async def muovi(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message("❌ Questo non è il tuo gioco!", ephemeral=True)
            return
        game = self.current_games[uid]
        game["posizione"] += 1
        pos = game["posizione"]
        traguardo = game["traguardo"]

        if pos >= traguardo:
            punti_guadagnati = random.randint(20, 100)
            punti_data[uid]["punti"] += punti_guadagnati
            save_punti()
            del self.current_games[uid]
            await interaction.response.send_message(
                content=f"🎉 Hai raggiunto il traguardo! Punti guadagnati: {punti_guadagnati}",
                view=None
            )
        else:
            barra = "🏃" + "—" * pos + "🏁" + "—" * (traguardo - pos)
            # Correzione qui
            await interaction.response.send_message(content=f"**Corsa:** {barra}", view=view)
            




        button_move = Button(label="Muovi", style=discord.ButtonStyle.green)
        button_move.callback = muovi
        view = View()
        view.add_item(button_move)
        barra_iniziale = "🏃" + "—" * 0 + "🏁" + "—" * 5
        await interaction.response.edit_message(content=f"**Corsa:** {barra}", view=view)
        




# ================= REGISTRA COG =================
async def setup():
    await bot.add_cog(Gioco(bot))
    await bot.start(TOKEN)

import asyncio
asyncio.run(setup())


# ================= AVVIO BOT =================
bot.run(TOKEN)
