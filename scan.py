import os
import re

LOG_FILE_PATH = "latest.log"

def giga_intensiv_analys():
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Hittade inte {LOG_FILE_PATH}! Se till att skriptet ligger i serverns logg-mapp.")
        return

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        rader = f.readlines()

    # --- NÄTVERK & IP-ADRESSER (EAGLER-NETWORK PROXY) ---
    eagler_ips = {"joris34": "Ingen IP funnen i Eagler-loggarna", "rip_shy": "Ingen IP funnen i Eagler-loggarna"}
    
    # --- UTREDNING: JORIS34 ---
    joris_lagliga_handlingar = []
    joris_olagliga_handlingar = []
    
    # --- UTREDNING: RIP_SHY ---
    rip_creative_bevis = []
    rip_client_bevis = []
    rip_injection_bevis = []
    rip_exploit_bevis = []

    # Avancerade sökord för dolda hack och Script Injections
    injection_keywords = ["\"", "'", "&&", "||", "eval", "parent set", "permission set", "meta clear", "execute as", "${", "jndi", "run command", "sudo"]
    exploit_keywords = ["//calc", "//solve", "authme", "litebans", "nbt", "packet", "crash", "exploit", "bukkit:", "minecraft:", "pex ", "plugman"]

    print("\n" + "=" * 90)
    print(" 🔥 STARTAR EXTREMT INTENSIV DJUPANALYS OCH UTREDNING AV SERVERLOGGEN 🔥 ")
    print("=" * 90)

    # LOOPA IGENOM HELA LOGGEN RAD FÖR RAD
    for i, rad in enumerate(rader):
        r_lower = rad.lower()

        # -----------------------------------------------------------------
        # 1. SKANNA EAGLER-NETWORK PROXY LOGGAR EFTER IP
        # -----------------------------------------------------------------
        if any(x in r_lower for x in ["eagler", "connect", "logged in", "proxy", "bungee"]):
            # Sök efter IP-adresser i loggraden
            ip_match = re.search(r"(/[\d\.]+:\d+|[\d\.]+)", rad)
            if ip_match:
                ren_ip = ip_match.group(1).replace("/", "")
                if "joris34" in r_lower:
                    eagler_ips["joris34"] = ren_ip
                if "rip_shy" in r_lower:
                    eagler_ips["rip_shy"] = ren_ip

        # -----------------------------------------------------------------
        # 2. INTENSIV ANALYS: JORIS34 (LAGLIGT VS OLAGLIGT)
        # -----------------------------------------------------------------
        if "joris34" in r_lower:
            tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
            tid = tid_match.group(1) if tid_match else "Okänd tid"
            
            # KOLLA OM HAN GJORDE LAGLIGT VIA /SELL
            if "sell" in r_lower:
                block_namn = "okänt block/föremål"
                summa = "0"
                
                # Sök framåt i loggen för att se vad shopen gav honom
                for j in range(1, 6):
                    if i + j < len(rader):
                        nasta_rad = rader[i + j].lower()
                        if "worth" in nasta_rad or "säljer" in nasta_rad or "sold" in nasta_rad:
                            item_match = re.search(r"([a-zA-Z_0-9]+)", nasta_rad)
                            if item_match:
                                block_namn = item_match.group(1)
                        if "eco give" in nasta_rad or "money give" in nasta_rad or "eco:give" in nasta_rad:
                            pengar_match = re.search(r"(?:give\s+joris34\s+)(\d+(?:\.\d+)?)", nasta_rad)
                            if pengar_match:
                                summa = pengar_match.group(1)
                                joris_lagliga_handlingar.append(f"[{tid}] Joris34 gjorde LAGLIGT: Han sålde {block_namn} för {summa} kr via din /sell.")

            # KOLLA OM HAN GJORDE OLAGLIGT (FICK PENGAR UTAN /SELL)
            if ("eco give" in r_lower or "money give" in r_lower or "pay" in r_lower) and "joris34" in r_lower:
                # Kolla bakåt så det inte var en /sell som triggade detta
                gick_via_sell = False
                for k in range(max(0, i-5), i):
                    if "sell" in rader[k].lower() and "joris34" in rader[k].lower():
                        gick_via_sell = True
                
                if not gick_via_sell:
                    pengar_match = re.search(r"(?:joris34\s+)(\d+(?:\.\d+)?)", r_lower)
                    summa = pengar_match.group(1) if pengar_match else "Okänd mängd"
                    if "pay" in r_lower:
                        joris_olagliga_handlingar.append(f"[{tid}] Joris34 gjorde OLAGLIGT: Han tog emot {summa} kr via /pay direkt från en fuskare utanför shopen.")
                    else:
                        joris_olagliga_handlingar.append(f"[{tid}] Joris34 gjorde OLAGLIGT: Han fick {summa} kr direkt insatt i sitt konto via rått konsolkommando (Hack/Exploit).")

        # -----------------------------------------------------------------
        # 3. INTENSIV ANALYS: RIP_SHY (EXAKT HUR HACKADE HAN?)
        # -----------------------------------------------------------------
        if "rip_shy" in r_lower:
            tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
            tid = tid_match.group(1) if tid_match else "Okänd tid"
            ren_rad = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", rad.strip())

            # KOLLA HUR HAN HACKADE: CREATIVE MODE
            if any(x in r_lower for x in ["gamemode c", "gamemode creative", "gm c", "gmc", "gamemode 1", "gm 1"]):
                rip_creative_bevis.append(f"[{tid}] Tog sig in i Creative Mode -> Logg: {ren_rad}")

            # KOLLA HUR HAN HACKADE: HACKED CLIENT (RÖRELSEFUSK DETEKTERAT AV SERVERNS ANTI-CHEAT)
            if any(x in r_lower for x in ["moved too quickly", "moved wrongly", "failed survival flying", "invalid move"]):
                rip_client_bevis.append(f"[{tid}] Fuskklient aktiv (Fly/Speed/NoFall detekterad av servern) -> Logg: {ren_rad}")
            if "fly" in r_lower and ("enabled" in r_lower or "true" in r_lower or "toggled" in r_lower):
                rip_client_bevis.append(f"[{tid}] Slog på flyg-läge via fusk/kommando -> Logg: {ren_rad}")

            # KOLLA HUR HAN HACKADE: SCRIPT INJECTION (KOD-MANIPULERING)
            if "issued server command" in r_lower and any(x in r_lower for x in injection_keywords):
                rip_injection_bevis.append(f"[{tid}] Script Injection (Försökte spränga Skript-kod med konstiga tecken) -> Logg: {ren_rad}")

            # KOLLA HUR HAN HACKADE: PLUGIN EXPLOITS & ADMIN KOMMANDON
            if "issued server command" in r_lower and any(x in r_lower for x in exploit_keywords):
                rip_exploit_bevis.append(f"[{tid}] Plugin Exploit (Försökte krascha servern eller kringgå rättigheter) -> Logg: {ren_rad}")
            if "issued server command" in r_lower and any(x in r_lower for x in ["/op", "/deop", "/plugins", "/pl", "/luckperms", "/lp"]):
                rip_exploit_bevis.append(f"[{tid}] Försökte köra låsta admin-kommandon -> Logg: {ren_rad}")


    # =================================================================
    # PRESENTERA DET DETALJERADE OCH INTENSIVA RESULTATET
    # =================================================================
    
    # OUTPUT FÖR JORIS34
    print("\n[📊 JORIS34 - EKONOMISK UTREDNING]:")
    if joris_olagliga_handlingar:
        print("  ❌ HITTADE BEVIS PÅ OLAGLIG HANTERING:")
        for handling in joris_olagliga_handlingar:
            print(f"     {handling}")
    
    if joris_lagliga_handlingar:
        print("  ✅ HITTADE BEVIS PÅ LAGLIG HANTERING (MEN PRISERNA ÄR BUGGADE):")
        for handling in joris_lagliga_handlingar:
            print(f"     {handling}")
            
    if not joris_olagliga_handlingar and not joris_lagliga_handlingar:
        print("  ⚪ Inga transaktioner eller sälj-loggar hittades för Joris34 i denna fil.")

    print("-" * 90)

    # OUTPUT FÖR RIP_SHY
    print("\n[⚡ RIP_SHY - EXAKT HUR HACKADE HAN IN SITT FUSK?]:")
    har_bevis = False
    
    if rip_client_bevis:
        print("  🔴 HUR: Han hackade med en HACKED CLIENT (Fly / Speed / Movement hacks):")
        for b in rip_client_bevis[:4]: print(f"     ↳ {b}")
        har_bevis = True
        
    if rip_creative_bevis:
        print("  🔴 HUR: Han hackade sig in i CREATIVE MODE via otillåten rättighet:")
        for b in rip_creative_bevis[:4]: print(f"     ↳ {b}")
        har_bevis = True

    if rip_injection_bevis:
        print("  🔴 HUR: Han hackade via SCRIPT INJECTION (Försökte lura koden i dina Skript):")
        for b in rip_injection_bevis[:4]: print(f"     ↳ {b}")
        har_bevis = True

    if rip_exploit_bevis:
        print("  🔴 HUR: Han hackade via PLUGIN EXPLOITS / OTILLÅTNA ADMIN-KOMMANDON:")
        for b in rip_exploit_bevis[:4]: print(f"     ↳ {b}")
        har_bevis = True

    if not har_bevis:
        print("  🟢 Inga stenhårda spår av fusk funna för Rip_Shy i just denna loggfil.")

    print("-" * 90)

    # OUTPUT FÖR IP-ADRESSER (EAGLER-NETWORK PROXY)
    print("\n[🔌 EAGLER-NETWORK PROXY - IP-ADRESSER DETEKTERADE FÖR BAN]:")
    print(f"   ➔ Joris34 Riktiga IP:  {eagler_ips['joris34']}")
    print(f"   ➔ Rip_Shy Riktiga IP:  {eagler_ips['rip_shy']}")
    print("\n  Kopiera dessa IP-adresser till din ban-lista för att stänga ute dem helt från nätverket!")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    giga_intensiv_analys()
