import os
import re

LOG_FILE_PATH = "latest.log"

def giga_intensiv_utredning():
    if not os.path.exists(LOG_FILE_PATH):
        print("Hittade inte latest.log! Lägg skriptet i rätt mapp.")
        return

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        rader = f.readlines()

    # --- IP ADRESSER (EAGLER-NETWORK PROXY LOGS) ---
    ip_adresser = {"joris34": "Hittade ingen IP i denna logg", "rip_shy": "Hittade ingen IP i denna logg"}

    # --- UTREDNING JORIS34 ---
    joris_dom = "INGA Transaktioner funna."
    joris_detaljer = []
    
    # --- UTREDNING RIP_SHY ---
    rip_metoder = set()
    rip_detaljer = []

    # Sökord för injektioner och fuskklienter
    injection_keywords = ["\"", "'", "&&", "||", "eval", "parent set", "permission set", "meta clear", "execute as", "${", "jndi"]
    exploit_keywords = ["//calc", "//solve", "authme", "nbt", "packet", "crash", "exploit", "bukkit:", "minecraft:", "pay *"]

    print("\n" + "=" * 90)
    print(" 🚨 STARTAR 10X INTENSIV UTREDNING: JORIS34, RIP_SHY & EAGLER PROXY IP-SKANNING 🚨 ")
    print("=" * 90)

    for i, rad in enumerate(rader):
        r_lower = rad.lower()
        
        # -----------------------------------------------------------------
        # STEG 1: SKANNA IP-ADRESSER (Eagler-Network / Bungee / Connect loggar)
        # -----------------------------------------------------------------
        if "eagler" in r_lower or "connect" in r_lower or "ip" in r_lower or "logged in" in r_lower:
            # Letar efter IP-mönster (t.ex. /12.34.56.78:12345 eller vanliga adresser)
            ip_match = re.search(r"(/[\d\.]+:\d+|[\d\.]+)?", rad)
            if ip_match and ip_match.group():
                hittad_ip = ip_match.group()
                if "joris34" in r_lower:
                    ip_adresser["joris34"] = hittad_ip
                if "rip_shy" in r_lower:
                    ip_adresser["rip_shy"] = hittad_ip

        # -----------------------------------------------------------------
        # STEG 2: EXAKT HUR GJORDE JORIS34? (LAGLIGT ELLER OLAGLIGT)
        # -----------------------------------------------------------------
        if "joris34" in r_lower:
            tid = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
            tid_str = tid.group(1) if tid else "Okänd tid"
            
            # Scenario A: Använde /sell (Kolla hur det gick till)
            if "sell" in r_lower:
                for j in range(1, 5):
                    if i + j < len(rader):
                        nasta_rad = rader[i + j].lower()
                        if "eco give" in nasta_rad or "money give" in nasta_rad:
                            pengar_match = re.search(r"(?:give\s+joris34\s+)(\d+(?:\.\d+)?)", nasta_rad)
                            summa = pengar_match.group(1) if pengar_match else "Okänd"
                            
                            joris_dom = f"🟢 LAGLIGT MEN UTNYTTJAT. Han använde din /sell-funktion."
                            joris_detaljer.append(f"[{tid_str}] HUR: Öppnade /sell -> Konsolen körde 'eco give' på {summa} kr direkt efteråt.")
                            break

            # Scenario B: Direkt kommando utan /sell (Olagligt / Insättning)
            if ("eco give" in r_lower or "money give" in r_lower or "pay" in r_lower) and "joris34" in r_lower:
                # Dubbelkolla bakåt så han inte nyss körde /sell
                hade_sell = False
                for k in range(max(0, i-4), i):
                    if "sell" in rader[k].lower() and "joris34" in rader[k].lower():
                        hade_sell = True
                
                if not hade_sell:
                    pengar_match = re.search(r"(?:joris34\s+)(\d+(?:\.\d+)?)", r_lower)
                    summa = pengar_match.group(1) if pengar_match else "Okänd"
                    
                    if "pay" in r_lower:
                        joris_dom = "🔴 OLAGLIGT! Han fick pengar skickade till sig utanför shopen."
                        joris_detaljer.append(f"[{tid_str}] HUR: Tog emot {summa} kr via /pay från en annan spelare (troligen Rip_Shy).")
                    else:
                        joris_dom = "🔴 OLAGLIGT! Någon tvingade konsolen att ge honom pengar bezpośrednio."
                        joris_detaljer.append(f"[{tid_str}] HUR: Konsolen körde rått kommando '/eco give joris34 {summa}' UTAN att han sålde block.")

        # -----------------------------------------------------------------
        # STEG 3: EXAKT HUR HACKADE RIP_SHY?
        # -----------------------------------------------------------------
        if "rip_shy" in r_lower:
            tid = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
            tid_str = tid.group(1) if tid else "Okänd tid"
            ren_rad = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", rad.strip())

            # Hur: Creative Mode
            if any(x in r_lower for x in ["gamemode c", "gamemode creative", "gm c", "gmc", "gamemode 1", "gm 1"]):
                rip_metoder.add("Creative Mode")
                rip_detaljer.append(f"[{tid_str}] HUR (Creative): Tvingade sig in i creative via kommandot: {ren_rad}")

            # Hur: Fly/Rörelsefusk
            if "fly" in r_lower and ("enabled" in r_lower or "true" in r_lower or "issued" in r_lower):
                rip_metoder.add("Fly-Kommando")
                rip_detaljer.append(f"[{tid_str}] HUR (Fly-Kommando): Aktiverade flygläge i servern: {ren_rad}")
                
            if any(x in r_lower for x in ["moved too quickly", "moved wrongly", "failed survival flying"]):
                rip_metoder.add("Hacked Client (Speed/Fly)")
                rip_detaljer.append(f"[{tid_str}] HUR (Fuskklient): Han rörde sig snabbare/annorlunda än vad Minecraft tillåter (Moved too quickly).")

            # Hur: Script Injection / Exploit
            if "issued server command" in r_lower:
                if any(x in r_lower for x in injection_keywords):
                    rip_metoder.add("Script Injection (Kod-manipulering)")
                    rip_detaljer.append(f"[{tid_str}] HUR (Script Injection): Använde otillåtna tecken för att bryta sönder dina Skript: {ren_rad}")
                if any(x in r_lower for x in exploit_keywords):
                    rip_metoder.add("Plugin Exploit (WorldEdit/Kraschförsök)")
                    rip_detaljer.append(f"[{tid_str}] HUR (Plugin Exploit): Körde farliga exploiter/kommandon: {ren_rad}")

    # =================================================================
    # PRESENTATION AV DE INTENSIVA SVAREN
    # =================================================================
    
    # 1. JORIS UTREDNING
    print("\n[📊 JORIS34 - EXAKT VAD OCH HUR GJORDE HAN?]")
    print(f"  DOM: {joris_dom}")
    if joris_detaljer:
        print("  TEKNISK BEVISNING OCH TIDSFÖRLOPP:")
        for d in joris_detaljer[:4]:
            print(f"    ↳ {d}")
    else:
        print("  Inga transaktioner hittades alls.")

    print("-" * 90)

    # 2. RIP_SHY UTREDNING
    print("\n[⚡ RIP_SHY - EXAFT HUR HACKADE HAN?]")
    if rip_metoder:
        print(f"  UPPTÄCKTA METODER: {', '.join(rip_metoder)}")
        print("  EXAKT HUR DET GICK TILL (FRÅN LOGGEN):")
        for d in rip_detaljer[:5]:
            print(f"    ↳ {d}")
    else:
        print("  🟢 Inga stenhårda spår av fusk funna för Rip_Shy i denna logg.")

    print("-" * 90)

    # 3. PROXY IP ADRESSER (FÖR ATT BANNA)
    print("\n[🔌 EAGLER-NETWORK PROXY LOG: IP-ADRESSER FÖR BAN]")
    print(f"  📌 Joris34 IP-Adress: {ip_adresser['joris34']}")
    print(f"  📌 Rip_Shy IP-Adress: {ip_adresser['rip_shy']}")
    print("\n  Använd dessa IP-adresser i din BungeeCord, Eagler-Proxy eller server för att IP-banna dem helt!")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    giga_intensiv_utredning()
