import os
import re

LOG_FILE_PATH = "latest.log"

def super_intensiv_analys():
    if not os.path.exists(LOG_FILE_PATH):
        print("Hittade inte latest.log! Se till att skriptet ligger i serverns logg-mapp.")
        return

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        rader = f.readlines()

    # --- VARIABLER FÖR JORIS34 ---
    joris_transaktioner = []
    total_lagliga_pengar = 0
    total_olagliga_pengar = 0
    joris_har_saljt = False

    # --- VARIABLER FÖR RIP_SHY (EXTREM SÖKNING) ---
    rip_bevis = {
        "creative_mode": [],
        "fly_hacks": [],
        "command_abuse": [],
        "script_injection": [],
        "vanilla_anti_cheat": [],
        "hacked_client_exploits": []
    }

    injection_keywords = [
        "\"", "'", "&&", "||", "eval", "parent set", "permission set", "meta clear", 
        "execute as", "run command", "sudo", "${", "jndi", "expr", "cancel event"
    ]
    
    exploit_keywords = [
        "//calc", "//solve", "authme", "litebans", "nbt", "packet", "crash", "exploit", 
        "bukkit:", "minecraft:", "pay *", "give *", "pex ", "plugman", "viaversion"
    ]

    for i, rad in enumerate(rader):
        r_lower = rad.lower()

        # =================================================================
        # DJUPANALYS: JORIS34 (FIXAD EXAKT PENGALÄSNING)
        # =================================================================
        if "joris34" in r_lower:
            if "sell" in r_lower:
                joris_har_saljt = True
                block_namn = "okänt föremål"
                summa = 0
                
                for j in range(1, 5):
                    if i + j < len(rader):
                        nasta_rad = rader[i + j].lower()
                        
                        if "worth" in nasta_rad or "säljer" in nasta_rad or "sold" in nasta_rad:
                            item_match = re.search(r"([a-zA-Z_0-9]+)", nasta_rad)
                            if item_match:
                                block_namn = item_match.group()

                        # Hämtar den exakta summan som getts i eco give direkt efter namnet
                        if "eco give" in nasta_rad or "money give" in nasta_rad or "eco:give" in nasta_rad:
                            pengar_match = re.search(r"(?:give\s+joris34\s+)(\d+(?:\.\d+)?)", nasta_rad)
                            if pengar_match:
                                summa = float(pengar_match.group(1))
                                total_lagliga_pengar += summa
                                joris_transaktioner.append(f"LAGLIGT: Sålde {block_namn} och fick ${summa:.2f} via /sell")
                                break

            if ("eco give" in r_lower or "money give" in r_lower or "pay" in r_lower) and "joris34" in r_lower:
                körde_sell_innan = False
                for k in range(max(0, i-4), i):
                    if "sell" in rader[k].lower() and "joris34" in rader[k].lower():
                        körde_sell_innan = True
                
                if not körde_sell_innan:
                    # Hämtar summan som getts utan /sell direkt efter namnet
                    pengar_match = re.search(r"(?:joris34\s+)(\d+(?:\.\d+)?)", r_lower)
                    if pengar_match:
                        s = float(pengar_match.group(1))
                        total_olagliga_pengar += s
                        joris_transaktioner.append(f"OLAGLIGT: Fick ${s:.2f} direkt via kommando/insättning")

        # =================================================================
        # DJUPANALYS: RIP_SHY
        # =================================================================
        if "rip_shy" in r_lower:
            tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
            tid = tid_match.group(1) if tid_match else "00:00:00"
            ren_rad = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", rad.strip())

            if any(x in r_lower for x in ["gamemode c", "gamemode creative", "gm c", "gmc", "gamemode 1", "gm 1"]):
                rip_bevis["creative_mode"].append(f"[{tid}] Enheten gick i Creative: {ren_rad}")

            if "fly" in r_lower and ("enabled" in r_lower or "true" in r_lower or "issued server command" in r_lower or "toggled" in r_lower):
                rip_bevis["fly_hacks"].append(f"[{tid}] Slog på flygläge: {ren_rad}")

            if any(x in r_lower for x in ["moved too quickly", "moved wrongly", "failed survival flying", "invalid move"]):
                rip_bevis["vanilla_anti_cheat"].append(f"[{tid}] Servern upptäckte fuskförflyttning: {ren_rad}")

            if "issued server command" in r_lower:
                if any(x in r_lower for x in ["/op", "/deop", "/plugins", "/pl", "/stop", "/sk", "/luckperms", "/lp", "/banned", "/ban", "/kick"]):
                    rip_bevis["command_abuse"].append(f"[{tid}] Försökte använda kritiskt admin-kommando: {ren_rad}")
                if any(x in r_lower for x in injection_keywords):
                    rip_bevis["script_injection"].append(f"[{tid}] INTENSIV SCRIPT INJECTION DETEKTERAD: {ren_rad}")
                if any(x in r_lower for x in exploit_keywords):
                    rip_bevis["hacked_client_exploits"].append(f"[{tid}] EXPLOIT / HACK CLIENT MÖNSTER: {ren_rad}")

    # =================================================================
    # PRESENTERA RESULTATET
    # =================================================================
    print("\n" + "=" * 75)
    print("      🔍 ULTRA-INTENSIV UTREDNINGS-RAPPORT FÖR SERVERN 🔍      ")
    print("=" * 75)

    print("\n[📊 JORIS34 EKONOMI-DOM]:")
    if total_olagliga_pengar > 0:
        print(f"  🔴 STATUS: OLAGLIGT! Han har tagit emot totalt {total_olagliga_pengar:.2f} kr direkt via dolda kommandon.")
    elif total_lagliga_pengar > 0:
        print(f"  🟢 STATUS: LAGLIGT PÅ SERVERN! Han tjänade totalt {total_lagliga_pengar:.2f} kr via din vanliga /sell-funktion.")
        print("            Det betyder att han bara sålde saker via ditt GUI (men priserna kan vara buggade).")
    elif len(joris_transaktioner) == 0:
        print("  ⚪ STATUS: Inga spår av pengatransaktioner hittades för Joris34 i denna loggfil.")
    
    if joris_transaktioner:
        print("  Ekonomiska händelser (Max 5 visas):")
        for t in joris_transaktioner[:5]:
            print(f"    -> {t}")

    print("-" * 75)
    print("\n[⚡ RIP_SHY EXTREM FUSK & HACK ANALYS]:")
    fusk_hittat = False
    
    if rip_bevis["script_injection"]:
        print("  🔴 [AKUT] SCRIPT INJECTION UPPTÄCKT!")
        for b in rip_bevis["script_injection"][:5]: print(f"      {b}")
        fusk_hittat = True
    if rip_bevis["hacked_client_exploits"]:
        print("  🔴 [AKUT] HACKED CLIENT / EXPLOITS DETEKTERAD:")
        for b in rip_bevis["hacked_client_exploits"][:5]: print(f"      {b}")
        fusk_hittat = True
    if rip_bevis["creative_mode"]:
        print("  🔴 CREATIVE MODE UTNYTTJAT:")
        for b in rip_bevis["creative_mode"][:5]: print(f"      {b}")
        fusk_hittat = True
    if rip_bevis["fly_hacks"] or rip_bevis["vanilla_anti_cheat"]:
        print("  🔴 RÖRELSEFUSK (Fly/Speed/Hacked Client):")
        for b in (rip_bevis["fly_hacks"] + rip_bevis["vanilla_anti_cheat"])[:5]: print(f"      {b}")
        fusk_hittat = True
    if rip_bevis["command_abuse"]:
        print("  ⚠️ OTILLÅTNA ADMIN-KOMMANDON:")
        for b in rip_bevis["command_abuse"][:5]: print(f"      {b}")
        fusk_hittat = True
    if not fusk_hittat:
        print("  🟢 Inga intensiva spår av fusk hittades för Rip_Shy.")

    print("=" * 75 + "\n")

if __name__ == "__main__":
    super_intensiv_analys()
