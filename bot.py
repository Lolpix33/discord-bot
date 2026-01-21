import discord
from discord.ext import commands, tasks
import json
import time
from datetime import timedelta
from datetime import datetime
import os

RANK_STEPS = [
    (0, "🔰 Nuovo Staff"),
    (5 * 3600, "⭐ Staff Intraprendente"),
    (10 * 3600, "🎖 Staff Attivo"),
    (30 * 3600, "🥉 Staff Avanzato"),
    (60 * 3600, "🥈 Staff Da esempio"),
    (100 * 3600, "🥇 Staff Esperto"),
    (250 * 3600, "🏆 Staff Unico"),
    (300 * 3600, "🏆 Staff Unico II"),
    (350 * 3600, "✨ Staff Galaxy"),
    (450 * 3600, "🌠 Staff Galattico"),
    (550 * 3600, "👑 Staff Principale del Server"),
    (1000 * 3600, "🌌 Staff Universale")
]


# ================== PATH DATI ==================
DATA_DIR = "data"
STAFF_FILE = os.path.join(DATA_DIR, "staff_hours.json")
PUNTI_FILE = os.path.join(DATA_DIR, "punti.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ================== STAFF DATA ==================

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
MODERATORI_ROLE_ID = 1382480385371537479
MODERATORI_AVANZATI_ROLE_ID = 1463517577111277813
ADMIN_ROLE_ID = 1462826237499277476
DIRETTORE_ROLE_ID = 1426308704759976108
MANAGER_ROLE_ID = 1459987923020677437
PROPRIETARIO_ID = 1382481167894450319


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
VC_CHANNEL_IDS = [
    1382496983713054790,
    1462108888945131753,
    1278033707457843319,
    1462928920000069732,
    1462929261777387552,
    1462929311412523038,
    1453555421691379796,
    1451579486477877268,
    1398840059846856804,
    1462930074637701180,
    1462930048398131281,
    1462930024926810286,
    1462927348587302962,
    1462927312046653651,
    1462927204089466901,
    1462927098296537211,
    1462927527235420353,
    1278033707457843320,
    1454875006692626454,
    1454209806134022321,
    1455658052437934222,
    1387804408917790800,
] #


DATA_FILE = "staff_hours.json"
YOUTUBE_LINK = "https://www.youtube.com/@Ombra130"
# ==========================================

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
    """a
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
def get_rank(seconds):
    current_rank = RANK_STEPS[0][1]

    for threshold, name in RANK_STEPS:
        if seconds >= threshold:
            current_rank = name
        else:
            break

    return current_rank




def rank_progress_bar(seconds):
    steps = RANK_STEPS

    # Rank massimo
    if seconds >= steps[-1][0]:
        return steps[-1][1], "🟦" * 20, 0

    current_rank = steps[0][1]
    current_threshold = steps[0][0]
    next_threshold = steps[1][0]

    for i in range(len(steps) - 1):
        if steps[i][0] <= seconds < steps[i + 1][0]:
            current_rank = steps[i][1]
            current_threshold = steps[i][0]
            next_threshold = steps[i + 1][0]
            break

    progress = (seconds - current_threshold) / (next_threshold - current_threshold)
    progress = max(0, min(progress, 1))

    filled = int(progress * 20)
    barra = "🟦" * filled + "⬜" * (20 - filled)

    mancanti = max(0, next_threshold - seconds)
    return current_rank, barra, mancanti





# ================= PERMESSI =================

def dm_check():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or any(
            r.id == ADV_MOD_ROLE_ID for r in ctx.author.roles
        )
    return commands.check(predicate)

def punishment_check():
    async def predicate(ctx):
        return (
            ctx.author.id in [MANAGER_ID, PROPRIETARIO_ID] or
            ctx.author.guild_permissions.administrator or
            any(r.id in [
                MODERATORI_ROLE_ID,
                MODERATORI_AVANZATI_ROLE_ID,
                ADMIN_ROLE_ID,
                DIRETTORE_ROLE_ID
            ] for r in ctx.author.roles)
        )
    return commands.check(predicate)

def owner_or_direttore_check():
    async def predicate(ctx):
        return (
            ctx.author.id in [PROPRIETARIO_ID, MANAGER_ID] or
            any(r.id == DIRETTORE_ROLE_ID for r in ctx.author.roles)
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
@punishment_check()
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
@punishment_check()
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
@punishment_check()
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
    "vc_minuti": 0,
    "vc_inizio": None,
    "avviso_vc": False

})


    channel = bot.get_channel(SERVICE_CHANNEL_ID)

    if stato.lower() == "on":
        if staff_data[uid]["inizio"]:
            return await ctx.reply("⚠️ Sei già in servizio")

        staff_data[uid]["inizio"] = now
        staff_data[uid]["vc_inizio"] = None
        staff_data[uid]["avviso_vc"] = False

        # 🔎 FIX: se è già in una VC staff, avvia il conteggio VC
        if ctx.author.voice and ctx.author.voice.channel:
            if ctx.author.voice.channel.id in VC_CHANNEL_IDS:
                staff_data[uid]["vc_inizio"] = now

        save_staff()

        embed = discord.Embed(
            title="🟢 ENTRATA IN SERVIZIO",
            description=f"👮 {ctx.author.mention} è ora **IN SERVIZIO**",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=embed)

    else:
        await ctx.reply("❌ NON ESISTE QUESTO COMANDO | DEVI USARE IL PANNELLO IN SERVIZIO STAFF E CLICCARE ENTRA IN SERVIZIO")

# ================= SERVIZIO CON BOTTONI =================

class ServizioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ================= ENTRA IN SERVIZIO =================
    @discord.ui.button(label="🟢 Mettiti in Servizio", style=discord.ButtonStyle.success)
    async def servizio_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        now = time.time()
        start_timestamp = int(now)


        def default_staff():
            return {
                "totale": 0,
                "inizio": None,
                "pausa": False,
                "messaggi": 0,
                "comandi": 0,
                "dm_gestiti": 0,
                "vc_minuti": 0,
                "vc_inizio": None,
                "avviso_vc": False
                
            }



        staff_data.setdefault(uid, {
            "totale": 0,
            "inizio": None,
            "pausa": False,
            "messaggi": 0,
            "comandi": 0,
            "dm_gestiti": 0,
            "vc_minuti": 0,
            "vc_inizio": None,
            "avviso_vc": False
        })

        if staff_data[uid]["inizio"] is not None:
            return await interaction.response.send_message("⚠️ Sei già in servizio", ephemeral=True)

        staff_data[uid]["inizio"] = now
        staff_data[uid]["vc_inizio"] = None
        staff_data[uid]["avviso_vc"] = False

        # 🔎 FIX VC: se è già in vocale staff
        if interaction.user.voice and interaction.user.voice.channel:
            if interaction.user.voice.channel.id in VC_CHANNEL_IDS:
                staff_data[uid]["vc_inizio"] = now

        save_staff()




        embed = discord.Embed(
            title="🟢 Entrata in servizio",
            description=f"👮 {interaction.user.mention} è entrato in servizio",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="⏱ Inizio servizio",
            value=f"<t:{start_timestamp}:R>",
            inline=False
        )

        # Notifica Owner
        try:
            await interaction.guild.owner.send(embed=embed)
        except:
            pass

        # Notifica Direttore
        direttore_role = interaction.guild.get_role(DIRETTORE_ROLE_ID)
        if direttore_role:
            for membro in direttore_role.members:
                try:
                    await membro.send(embed=embed)
                except:
                    pass

        await interaction.response.send_message(
            f"🟢 **Servizio attivato con successo**\n\n"
            f"👮 Sei entrato in servizio **da:**\n"
            f"⏱ <t:{start_timestamp}:R>\n\n"
            f"🔔 Il tempo verrà conteggiato automaticamente.",
            ephemeral=True
        )

    # ================= ESCI DAL SERVIZIO =================
    @discord.ui.button(label="🔴 Esci dal Servizio", style=discord.ButtonStyle.danger)
    async def servizio_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = str(interaction.user.id)
        now = time.time()

        if uid not in staff_data or staff_data[uid]["inizio"] is None:
            return await interaction.response.send_message("⚠️ Non sei in servizio", ephemeral=True)

        # Calcola durata sessione
        inizio_sessione = staff_data[uid]["inizio"]
        durata_sessione = now - inizio_sessione
        staff_data[uid]["totale"] += durata_sessione

        # ---------- CALCOLO VC ----------
        inizio_vc = staff_data[uid].get("vc_inizio")
        if inizio_vc:
            staff_data[uid]["vc_minuti"] += int(now - inizio_vc)
            staff_data[uid]["vc_inizio"] = None

        # Reset stato
        staff_data[uid]["inizio"] = None
        staff_data[uid]["pausa"] = False
        staff_data[uid]["vc_inizio"] = None
        save_staff()

        # ---------- EMBED ----------
        embed = discord.Embed(
            title=f"🔴 {interaction.user.display_name} è uscito dal servizio",
            description=(
                f"👮 **Staff:** {interaction.user.mention}\n"
                f"⏱ **Durata sessione:** {format_time(durata_sessione)}\n"
                f"⏱ **Ore totali:** {format_time(staff_data[uid]['totale'])}\n"
                f"🏅 **Rank attuale:** {get_rank(staff_data[uid]['totale'])}\n"
                f"💬 **Messaggi inviati:** {staff_data[uid]['messaggi']}\n"
                f"⚡ **Comandi usati:** {staff_data[uid]['comandi']}\n"
                f"✉️ **DM gestiti:** {staff_data[uid]['dm_gestiti']}\n"
                f"🎤 **Secondi in VC:** {format_time(staff_data[uid]['vc_minuti'])}\n"
                f"🕒 **Inizio sessione:** {datetime.fromtimestamp(inizio_sessione).strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        # ================= NOTIFICHE =================
        # Owner
        try:
            await interaction.guild.owner.send(embed=embed)
        except:
            pass

        # Direttore
        direttore_role = interaction.guild.get_role(DIRETTORE_ROLE_ID)
        if direttore_role:
            for membro in direttore_role.members:
                try:
                    await membro.send(embed=embed)
                except:
                    pass

        # Manager (COME DIRETTORE, A RUOLO)
        manager_role = interaction.guild.get_role(MANAGER_ROLE_ID)
        if manager_role:
            for membro in manager_role.members:
                try:
                    await membro.send(embed=embed)
                except:
                    pass






        # ---------- RISPOSTA ALL'UTENTE ----------
        rank, barra, mancanti = rank_progress_bar(staff_data[uid]["totale"])

        progresso_text = (
            "🏆 **Hai raggiunto il rank massimo!**"
            if mancanti == 0
            else f"⏳ **Ore al prossimo rank:** {format_time(mancanti)}"
        )

        await interaction.response.send_message(
            f"🔴 **Sei uscito dal servizio**\n\n"
            f"⏱ **Durata sessione:** {format_time(durata_sessione)}\n"
            f"⏱ **Ore totali:** {format_time(staff_data[uid]['totale'])}\n"
            f"🏅 **Rank attuale:** {rank}\n\n"
            f"{barra}\n"
            f"{progresso_text}",
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

    embed = discord.Embed(
        title="📊 Report Staff Ombra del 130",
        description="Ecco le ore e i rank di tutto lo staff con progresso verso il prossimo rank!",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    )

    for membro in ruolo_staff.members:
        uid = str(membro.id)
        totale = staff_data.get(uid, {}).get("totale", 0)

        rank, barra, mancanti = rank_progress_bar(totale)

        if mancanti == 0:
            progresso = "🏆 Rank massimo raggiunto"
        else:
            progresso = f"⏳ Ore al prossimo rank: **{format_time(mancanti)}**"

        embed.add_field(
            name=f"👤 {membro.display_name}",
            value=(
                f"🏅 Rank: **{rank}**\n"
                f"⏱ Ore totali: **{format_time(totale)}**\n"
                f"{barra}\n"
                f"{progresso}"
            ),
            inline=False
        )

    embed.set_footer(text="💡 Comando eseguibile solo da Owner o Direttore")
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
async def invia_classifica_staff():
    channel = bot.get_channel(PROMO_CHANNEL_ID)
    if not channel:
        return

    guild = bot.get_guild(MAIN_GUILD_ID)
    if not guild:
        return

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

    await channel.send(embed=embed)


@tasks.loop(minutes=210)
async def vetrina_rank_staff():
    now = datetime.now().time()
    start_time = datetime.strptime("12:00", "%H:%M").time()
    end_time = datetime.strptime("23:00", "%H:%M").time()

    if not (start_time <= now <= end_time):
        return

    await invia_classifica_staff()


@tasks.loop(minutes=1)
async def vc_heartbeat():
    now = time.time()

    for uid, dati in staff_data.items():
        if not dati.get("inizio"):
            continue

        vc_start = dati.get("vc_inizio")
        if vc_start:
            dati["vc_minuti"] += int(now - vc_start)
            dati["vc_inizio"] = now

    save_staff()


# ================= ON READY =================

@bot.event
async def on_ready():
    guild_ids = [g.id for g in bot.guilds]

    if MAIN_GUILD_ID not in guild_ids:
        print("❌ Bot avviato in un server NON autorizzato")
        await bot.close()
        return

    print(f"🤖 {bot.user} ONLINE nel server autorizzato")

    if not promozione_youtube.is_running():
        promozione_youtube.start()

    if not promemoria_staff.is_running():
        promemoria_staff.start()

    if not vetrina_rank_staff.is_running():
        vetrina_rank_staff.start()

    if not vc_heartbeat.is_running():
        vc_heartbeat.start()

    # 🔥 QUESTA È LA RIGA CHE SISTEMA TUTTO
    await invia_classifica_staff()






# ================= ON_MESSAGE =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = str(message.author.id)

    # ---------- MESSAGGI IN SERVER (conteggio staff) ----------
    if message.guild and uid in staff_data:
        if staff_data[uid].get("inizio") and not staff_data[uid].get("pausa"):
            staff_data[uid]["messaggi"] += 1

    # ---------- MESSAGGI IN DM ----------
    if isinstance(message.channel, discord.DMChannel):
        staff_channel = bot.get_channel(STAFF_CHANNEL_ID)

        # Log DM allo staff
        if staff_channel:
            embed = discord.Embed(
                title="📩 NUOVO MESSAGGIO AL BOT",
                color=discord.Color.dark_gold(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👤 Utente", value=f"{message.author} (`{message.author.id}`)", inline=False)
            embed.add_field(name="💬 Messaggio", value=message.content or "*[Allegato o vuoto]*", inline=False)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="DM ricevuto • Staff Ombra del 130")
            await staff_channel.send(embed=embed)

        # Conta DM gestito da uno solo staff in servizio
        for staff_uid, dati in staff_data.items():
            if dati.get("inizio") and not dati.get("pausa"):
                dati["dm_gestiti"] += 1
                break  # solo uno staff prende il DM

        # Risposta automatica
        try:
            await message.author.send(
                "✅ **Messaggio ricevuto!**\n👀 Lo staff sta leggendo la tua richiesta.\n⏳ Ti risponderemo presto."
            )
        except:
            pass

    # Salva tutto alla fine
    save_staff()

    # ---------- PROCESSA COMANDI ----------
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    uid = str(member.id)
    dati = staff_data.get(uid)

    if not dati or not dati.get("inizio"):
        return

    now = time.time()

    before_id = before.channel.id if before.channel else None
    after_id = after.channel.id if after.channel else None

    # ===== USCITA DA VC STAFF =====
    if before_id in VC_CHANNEL_IDS and after_id != before_id:
        inizio = dati.get("vc_inizio")
        if inizio:
            dati["vc_minuti"] += int(now - inizio)
            dati["vc_inizio"] = None

    # ===== ENTRATA IN VC STAFF =====
    if after_id in VC_CHANNEL_IDS and before_id != after_id:
        if not dati.get("vc_inizio"):
            dati["vc_inizio"] = now

    save_staff()


# ================= AVVIO BOT =================
bot.run(TOKEN)
