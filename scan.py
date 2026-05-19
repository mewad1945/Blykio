import os
import re

# Sökvägar till de olika loggfilerna
SMP_LOG = "latest.log"

# Lista på vanliga ställen där Eagler-proxyns/Bungeecords loggar kan ligga i förhållande till smp/logs
PROXY_SOKVAGAR = [
    "../../logs/latest.log",
    "../proxy/logs/latest.log",
    "../../proxy/logs/latest.log",
    "proxy.log",
    "./proxy.log"
]

def giga_intensiv_utredning():
    print("\n" + "=" * 95)
    print(" 🚨 [ULTRA-INTENSIV UTREDNING] INTEGRERAD SKANNING AV PROXY- LOGGAR OCH MINECRAFT-LOGGAR 🚨 ")
    print("=" * 95)

    # Förbered ordlistor för att spara IP-adresser
    eagler_ips = {
        "joris34": "Ingen IP funnen i Eagler-proxyns loggfiler", 
        "rip_shy": "Ingen IP funnen i Eagler-proxyns loggfiler"
    }
    
    proxy_fil_hittad = False
    proxy_rader = []

    # --- STEG 1: SÖK EFTER OCH LÄS IN EAGLER-NETWORK PROXY-LOGGEN ---
    for sokvag in PROXY_SOKVAGAR:
        if os.path.exists(sokvag):
            try:
                with open(sokvag, "r", encoding="utf-8", errors="ignore") as f:
                    proxy_rader = f.readlines()
                proxy_fil_hittad = True
                break
            except Exception:
                continue

    # Om vi hittade proxyloggar, leta efter de riktiga nätverks-IP-adresserna
    if proxy_fil_hittad:
        for rad in proxy_rader:
            r_lower = rad.lower()
            if any(x in r_lower for x in ["connect", "logged in", "initial handler", "eagler"]):
                # Letar efter mönster som [/123.45.67.89:54321] eller bara rena IP-adresser
                ip_match = re.search(r"(/[\d\.]+:\d+|[\d\.]+)", rad)
                if ip_match:
                    # Rensa bort snedstreck och portnummer för att få en ren IP-adress
                    ren_ip = ip_match.group(1).replace("/", "").split(":")[0]
                    if "joris34" in r_lower:
                        eagler_ips["joris34"] = ren_ip
                    if "rip_shy" in r_lower:
                        eagler_ips["rip_shy"] = ren_ip

    # --- STEG 2: SÖK IGENOM MINECRAFT SMP-LOGGEN EFTER FUSK-MÖNSTER ---
    if not os.path.exists(SMP_LOG):
        print(f" Fel: Hittade inte Minecraft-serverns loggfil ({SMP_LOG}).")
        print(" Se till att du kör detta skript inifrån mappen: ~/eagler-network/smp/logs/")
        return

    with open(SMP_LOG, "r", encoding="utf-8", errors="ignore") as f:
        smp_rader = f.readlines()

    # Variabler för att samla exakt bevisdata
    joris_handlingar = []
    rip_handlingar = []

    injection_keywords = ["\"", "'", "&&", "||", "eval", "parent set", "permission set", "meta clear", "execute as", "${", "jndi", "run command", "sudo"]
    exploit_keywords = ["//calc", "//solve", "authme", "litebans", "nbt", "packet", "crash", "exploit", "bukkit:", "minecraft:", "pex ", "plugman"]

    for i, rad in enumerate(smp_rader):
        r_lower = rad.lower()
        
        # Hämta tidstämpel från raden om den finns
        tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
        tid = tid_match.group(1) if tid_match else "Okänd tid"
        
        # Ta bort tidstämpeln från texten för att göra loggutskriften renare
        ren_rad = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", rad.strip())

        # --- GRANSKNING: JORIS34 ---
        if "joris34" in r_lower:
            # Kolla om han sålde via /sell GUI-menyn
            if "sell" in r_lower:
                block_namn = "okänt block/föremål"
                summa = "0"
                
                # Sök framåt i loggen (upp till 5 rader) för att se vad shopen gav honom
                for j in range(1, 6):
                    if i + j < len(smp_rader):
                        nasta_rad = smp_rader[i + j].lower()
                        if any(x in nasta_rad for x in ["worth", "säljer", "sold"]):
                            item_match = re.search(r"([a-zA-Z_0-9]+)", nasta_rad)
                            if item_match:
                                block_namn = item_match.group(1)
                        if any(x in nasta_rad for x in ["eco give", "money give", "eco:give"]):
                            pengar_match = re.search(r"(?:give\s+joris34\s+)(\d+(?:\.\d+)?)", nasta_rad)
                            if pengar_match:
                                summa = pengar_match.group(1)
                                joris_handlingar.append(f"[{tid}] LAGLIGT: Joris34 sålde {block_namn} för ${summa} via din /sell.")
                                break

            # Kolla om han tog emot pengar UTAN att använda /sell shopen
            if any(x in r_lower for x in ["eco give", "money give", "pay"]) and "joris34" in r_lower:
                # Säkerställ att det inte fanns ett säljkommando precis ovanför som utlöste det
                gick_via_sell = False
                for k in range(max(0, i-5), i):
                    if "sell" in smp_rader[k].lower() and "joris34" in smp_rader[k].lower():
                        gick_via_sell = True
                
                if not gick_via_sell:
                    pengar_match = re.search(r"(?:joris34\s+)(\d+(?:\.\d+)?)", r_lower)
                    summa = pengar_match.group(1) if pengar_match else "Okänd mängd"
                    
                    if "pay" in r_lower:
                        joris_handlingar.append(f"[{tid}] OLAGLIGT: Joris34 tog emot ${summa} direkt via /pay från en annan spelare utanför shopen.")
                    else:
                        joris_handlingar.append(f"[{tid}] OLAGLIGT: Joris34 fick ${summa} direkt insatt via rått konsolkommando (Skript-fel/Exploit) utan att sälja något.")

        # --- GRANSKNING: RIP_SHY ---
        if "rip_shy" in r_lower:
            # 1. Koll efter Creative Mode-hack
            if any(x in r_lower for x in ["gamemode c", "gamemode creative", "gm c", "gmc", "gamemode 1", "gm 1"]):
                rip_handlingar.append(f"[{tid}] HACKED CLIENT / CHEAT: Gick in i Creative Mode -> Logg: {ren_rad}")

            # 2. Koll efter Fly/Speed rörelsefusk detekterat av servern
            if any(x in r_lower for x in ["moved too quickly", "moved wrongly", "failed survival flying", "invalid move"]):
                rip_handlingar.append(f"[{tid}] HACKED CLIENT (Fly/Speed/NoFall detekterat av servern) -> Logg: {ren_rad}")
            if "fly" in r_lower and any(x in r_lower for x in ["enabled", "true", "toggled"]):
                rip_handlingar.append(f"[{tid}] HACKED CLIENT (Aktiverade flygläge via fusk/kommando) -> Logg: {ren_rad}")

            # 3. Koll efter Script Injections (Skadlig kod i kommandon/chatt)
            if "issued server command" in r_lower and any(x in r_lower for x in injection_keywords):
                rip_handlingar.append(f"[{tid}] SCRIPT INJECTION (Försökte skriva skadliga tecken för att bryta sönder Skript-kod) -> Logg: {ren_rad}")

            # 4. Koll efter Plugin Exploits & Otillåtna Admin-kommandon
            if "issued server command" in r_lower and any(x in r_lower for x in exploit_keywords):
                rip_handlingar.append(f"[{tid}] PLUGIN EXPLOIT (Försökte krascha servern eller utnyttja sårbarheter) -> Logg: {ren_rad}")
            if "issued server command" in r_lower and any(x in r_lower for x in ["/op", "/deop", "/plugins", "/pl", "/luckperms", "/lp"]):
                rip_handlingar.append(f"[{tid}] ADMIN COMMAND ABUSE (Försökte köra låsta admin-kommandon) -> Logg: {ren_rad}")


    # --- PRESENTERA DE ULTRA-INTENSIVA SVAREN ---
    print("\n" + "-" * 95)
    print(" 📊 UTREDNINGENS RESULTAT OCH BEVISDATA FÖR JORIS34:")
    print("-" * 95)
    if joris_handlingar:
        # Visar de händelser som hittades
        for h i, handling in enumerate(joris_handlingar):
            print(f"  {handling}")
    else:
        print("  ⚪ Inga ekonomiska händelser, köp eller fusk-insättningar hittades för Joris34 i denna fil.")

    print("\n" + "-" * 95)
    print(" ⚡ UTREDNINGENS RESULTAT OCH BEVISDATA FÖR RIP_SHY:")
    print("-" * 95)
    if rip_handlingar:
        # Visar de händelser som hittades
        for h i, handling in enumerate(rip_handlingar):
            print(f"  {handling}")
    else:
        print("  🟢 Inga stenhårda spår av fusk, rörelsemanipulering eller injektioner funna för Rip_Shy i denna fil.")

    print("\n" + "-" * 95)
    print(" 🔌 EAGLER-NETWORK PROXY LOGS - IP-ADRESSER DETEKTERADE FÖR BAN:")
    print("-" * 95)
    print(f"  📌 Spelare Joris34 Riktiga IP-Adress:  {eagler_ips['joris34']}")
    print(f"  📌 Spelare Rip_Shy Riktiga IP-Adress:  {eagler_ips['rip_shy']}")
    print("\n  [INFO]: Om IP:n visar 'Ingen IP funnen i Eagler-proxyns loggfiler', kopiera filen latest.log")
    print("  från din bungeecord/proxy-mapp till denna mapp och döp om den till proxy.log, kör sedan igen!")
    print("=" * 95 + "\n")

if __name__ == "__main__":
    giga_intensiv_utredning()
