import discord
from discord.ext import commands, tasks
import json
import time
from datetime import timedelta
from datetime import datetime
import os

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")


PREFIX = "!"

ADV_MOD_ROLE_ID = 1399839659961618513   # Ruolo che può usare DM / DM RUOLO
SERVICE_ROLE_ID = 1450228259018113187   # Ruolo staff
STAFF_CHANNEL_ID = 1399142358116995173  # Log DM
SERVICE_CHANNEL_ID = 1450225638224171090 # Log servizio
GENERAL_CHANNEL_ID = 1385409744444981389 # Generale per messaggi automatici

PROMO_CHANNEL_ID = 1385409744444981389  # Canale per messaggi YouTube
STAFF_REMINDER_CHANNEL_ID = 1399142358116995173 # Canale promemoria staff

ORESTAFF_ROLE_ID = 1426308704759976108 # Ruolo che può usare !orestaff

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
try:
    with open(DATA_FILE, "r") as f:
        staff_data = json.load(f)
except:
    staff_data = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(staff_data, f, indent=4)

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
    staff_data.setdefault(uid, {"totale": 0, "inizio": None})
    channel = bot.get_channel(SERVICE_CHANNEL_ID)

    if stato.lower() == "on":
        if staff_data[uid]["inizio"]:
            return await ctx.reply("⚠️ Sei già in servizio")
        staff_data[uid]["inizio"] = now
        save_data()
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
        save_data()
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

        staff_data.setdefault(uid, {"totale": 0, "inizio": None, "pausa": False})

        if staff_data[uid]["inizio"] and not staff_data[uid].get("pausa"):
            return await interaction.response.send_message(
                "⚠️ Sei già in servizio", ephemeral=True
            )

        staff_data[uid]["inizio"] = now
        staff_data[uid]["pausa"] = False
        save_data()

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
            save_data()
            button.label = "🟡 Pausa Servizio"  # Cambia label bottone
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("🟢 **Hai ripreso il servizio**", ephemeral=True)
        else:
            # Metti in pausa
            durata = time.time() - staff_data[uid]["inizio"]
            staff_data[uid]["totale"] += durata
            staff_data[uid]["pausa"] = True
            staff_data[uid]["inizio"] = None
            save_data()
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
        save_data()

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
@founder_check()
async def aggiungiore(ctx, member: discord.Member, ore: float):
    uid = str(member.id)
    staff_data.setdefault(uid, {"totale": 0, "inizio": None})
    staff_data[uid]["totale"] += ore * 3600
    save_data()
    await ctx.send(f"✅ Aggiunte {ore} ore a {member.mention}")

@bot.command()
@founder_check()
async def togliore(ctx, member: discord.Member, ore: float):
    uid = str(member.id)
    if uid not in staff_data:
        return await ctx.send("❌ Nessun dato trovato")
    staff_data[uid]["totale"] = max(
        0, staff_data[uid]["totale"] - ore * 3600
    )
    save_data()
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
    # Ignora i messaggi del bot stesso
    if message.author.bot:
        return

    # SOLO MESSAGGI IN PRIVATO
    if isinstance(message.channel, discord.DMChannel):
        staff_channel = bot.get_channel(STAFF_CHANNEL_ID)

        if staff_channel:
            embed = discord.Embed(
                title="📩 NUOVO MESSAGGIO INVIATO AL BOT DA UN UTENTE",
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
                value=message.content if message.content else "*[Messaggio vuoto / allegato]*",
                inline=False
            )

            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="📌 DM ricevuto dal bot • Staff Ombra del 130")

            await staff_channel.send(embed=embed)

        # RISPOSTA AUTOMATICA ALL’UTENTE
        try:
            await message.author.send(
                "✅ **Messaggio ricevuto!**\n\n"
                "👀 Lo **staff sta leggendo** la tua richiesta.\n"
                "🛠️ A breve verificheremo se sarà necessario fornirti **supporto**.\n\n"
                "⏳ Grazie per la pazienza!"
            )
        except:
            pass

    # FONDAMENTALE: permette ai comandi di funzionare
    await bot.process_commands(message)

# ================= GIOCO PUNTI =================
PUNTI_FILE = "punti.json"
GESTORE_PUNTI_ROLE_IDS = [SERVICE_ROLE_ID, 1454559530020245504]  # Tu + addetto punti

# Carica dati
try:
    with open(PUNTI_FILE, "r") as f:
        punti_data = json.load(f)
except:
    punti_data = {}

def save_punti():
    with open(PUNTI_FILE, "w") as f:
        json.dump(punti_data, f, indent=4)

def punti_check():
    async def predicate(ctx):
        return any(r.id in GESTORE_PUNTI_ROLE_IDS for r in ctx.author.roles) or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# ================= GIOCO UFFICIALE DI OMBRA DEL 130 =================
import random

PUNTI_FILE = "punti.json"
GESTORE_PUNTI_ROLE_IDS = [SERVICE_ROLE_ID, 1454559530020245504]  # Tu + addetto punti

# Carica dati
try:
    with open(PUNTI_FILE, "r") as f:
        punti_data = json.load(f)
except:
    punti_data = {}

def save_punti():
    with open(PUNTI_FILE, "w") as f:
        json.dump(punti_data, f, indent=4)

def punti_check():
    async def predicate(ctx):
        return any(r.id in GESTORE_PUNTI_ROLE_IDS for r in ctx.author.roles) or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# ======== Lista sfide (150+) ========
sfide = [
    {"domanda": "Qual è la capitale d'Italia?", "risposta": "roma"},
    {"domanda": "Quanto fa 7 x 8?", "risposta": "56"},
    {"domanda": "Scrivi il contrario di 'buio'", "risposta": "chiaro"},
    {"domanda": "Quale pianeta è il più vicino al Sole?", "risposta": "mercurio"},
    {"domanda": "Quante lettere ci sono nell'alfabeto italiano?", "risposta": "21"},
    {"domanda": "Scrivi la parola 'pippo' al contrario", "risposta": "oppip"},
    {"domanda": "Qual è il colore del sole?", "risposta": "giallo"},
    {"domanda": "Quanti continenti ci sono?", "risposta": "7"},
    {"domanda": "Che animale è il simbolo di Snapchat?", "risposta": "fantasma"},
    {"domanda": "Qual è la lingua più parlata al mondo?", "risposta": "cinese"},
    {"domanda": "Quanti pianeti ci sono nel sistema solare?", "risposta": "8"},
    {"domanda": "In quale anno è stata scoperta l'America?", "risposta": "1492"},
    {"domanda": "Qual è il numero di colori dell'arcobaleno?", "risposta": "7"},
    {"domanda": "Qual è l’animale più veloce sulla terra?", "risposta": "ghepardo"},
    {"domanda": "Quale gas respiriamo principalmente?", "risposta": "ossigeno"},
    {"domanda": "Qual è la moneta dell'Italia?", "risposta": "euro"},
    {"domanda": "Che colore ha l’acqua pura?", "risposta": "trasparente"},
    {"domanda": "Quanti giorni ha un anno bisestile?", "risposta": "366"},
    {"domanda": "Scrivi 'ciao' al contrario", "risposta": "oaic"},
    {"domanda": "Quanti giocatori ci sono in una squadra di calcio?", "risposta": "11"},
    {"domanda": "Qual è la capitale della Francia?", "risposta": "parigi"},
    {"domanda": "Chi ha scritto 'La Divina Commedia'?", "risposta": "dante"},
    {"domanda": "Quanto fa 12 + 15?", "risposta": "27"},
    {"domanda": "Quale elemento chimico ha il simbolo H?", "risposta": "idrogeno"},
    {"domanda": "Che colore ha il cielo?", "risposta": "azzurro"},
    {"domanda": "Qual è il fiume più lungo del mondo?", "risposta": "nilo"},
    {"domanda": "Qual è l’animale simbolo dell’Australia?", "risposta": "canguro"},
    {"domanda": "Quanti mesi ci sono in un anno?", "risposta": "12"},
    {"domanda": "Chi ha inventato la lampadina?", "risposta": "edison"},
    {"domanda": "Qual è la montagna più alta del mondo?", "risposta": "everest"},
    {"domanda": "Che numero viene dopo il 99?", "risposta": "100"},
    # ... aggiungi tutte le altre sfide fino a 150+ ...
]

# Genera automaticamente sfide dummy fino a 150
for i in range(len(sfide), 150):
    sfide.append({"domanda": f"Domanda casuale #{i+1}", "risposta": "risposta"})

# --------- COMANDO GIOCA ---------
@bot.command()
async def gioca(ctx):
    """Gioco ufficiale di Ombra del 130: rispondi alle sfide e guadagna punti!"""
    uid = str(ctx.author.id)
    punti_data.setdefault(uid, {"punti": 0})

    sfida = random.choice(sfide)
    domanda = sfida["domanda"]
    risposta_corretta = sfida["risposta"].lower()

    embed = discord.Embed(
        title="🎮 GIOCO UFFICIALE DI OMBRA DEL 130",
        description=f"👤 {ctx.author.mention}, ecco la tua sfida:\n\n**{domanda}**",
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        risposta = await bot.wait_for("message", timeout=30.0, check=check)
    except:
        await ctx.send(f"⏰ Tempo scaduto! La risposta corretta era: **{risposta_corretta}**")
        return

    if risposta.content.lower() == risposta_corretta:
        punti_guadagnati = random.randint(10, 50)
        punti_data[uid]["punti"] += punti_guadagnati
        save_punti()
        await ctx.send(f"✅ Bravo! Hai guadagnato **{punti_guadagnati} punti**. Totale punti: **{punti_data[uid]['punti']}**")
    else:
        await ctx.send(f"❌ Sbagliato! La risposta corretta era: **{risposta_corretta}**. Totale punti: **{punti_data[uid]['punti']}**")

# --------- COMANDO MOSTRA PUNTI ---------
@bot.command()
async def punti(ctx, member: discord.Member = None):
    member = member or ctx.author
    uid = str(member.id)
    tot = punti_data.get(uid, {}).get("punti", 0)
    embed = discord.Embed(
        title=f"💎 Punti di {member.display_name}",
        description=f"🏆 Totale punti: **{tot}**",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

# --------- COMANDI GESTIONE PUNTI ---------
@bot.command()
@punti_check()
async def aggiungipunti(ctx, member: discord.Member, punti: int):
    uid = str(member.id)
    punti_data.setdefault(uid, {"punti": 0})
    punti_data[uid]["punti"] += punti
    save_punti()
    await ctx.send(f"✅ Aggiunti {punti} punti a {member.mention}. Totale: {punti_data[uid]['punti']}")

@bot.command()
@punti_check()
async def togli_punti(ctx, member: discord.Member, punti: int):
    uid = str(member.id)
    punti_data.setdefault(uid, {"punti": 0})
    punti_data[uid]["punti"] = max(0, punti_data[uid]["punti"] - punti)
    save_punti()
    await ctx.send(f"⛔ Tolti {punti} punti a {member.mention}. Totale: {punti_data[uid]['punti']}")

# ================= AVVIO =================
bot.run(TOKEN)
