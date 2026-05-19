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

    # --- VARIABLER FÖR RIP_SHY (FUSK & INJEKTIONER) ---
    rip_bevis = {
        "creative_mode": [],
        "fly_hacks": [],
        "command_abuse": [],
        "script_injection": [],
        "vanilla_anti_cheat": [] # Fångar upp serverns egna dolda varningar om rörelse
    }

    # Sökord för kända injektioner eller försök att lura Skript/LuckPerms
    injection_keywords = ["\"", "'", "&&", "||", "eval", "parent set", "permission set", "meta clear", "execute as"]

    # Loopa igenom loggen rad för rad med index för tidslinjeanalys
    for i, rad in enumerate(rader):
        r_lower = rad.lower()

        # =================================================================
        # DJUPANALYS: JORIS34 (KOLLA OM DET VAR EN RIGGAD ELLER LAGLIG /SELL)
        # =================================================================
        if "joris34" in r_lower:
            # 1. Kolla om han startade en försäljning
            if "sell" in r_lower:
                joris_har_saljt = True
                
                # Sök framåt efter föremål och pengar (precis som på din bild)
                block_namn = "okänt föremål"
                summa = 0
                
                for j in range(1, 5):
                    if i + j < len(rader):
                        nasta_rad = rader[i + j].lower()
                        
                        # Försök fånga upp blocket/itemet (letar efter vanliga föremål eller 'worth')
                        if "worth" in nasta_rad or "säljer" in nasta_rad or "sold" in nasta_rad:
                            # Enkel regex för att hitta ord som liknar föremålsnamn
                            item_match = re.search(r"([a-zA-Z_]+)(beef|meat|dirt|stone|diamond|iron|gold|block|item)", nasta_rad)
                            if item_match:
                                block_namn = item_match.group()

                        # Fånga upp konsolens eco give direkt efteråt
                        if "eco give" in nasta_rad or "money give" in nasta_rad:
                            pengar_match = re.search(r"\d+(\.\d+)?", nasta_rad)
                            if pengar_match:
                                summa = float(pengar_match.group())
                                total_lagliga_pengar += summa
                                joris_transaktioner.append(f"LAGLIGT: Sålde {block_namn} och fick ${summa:.2f} via /sell")
                                break

            # 2. Kolla om han fick pengar UTAN att ha kört /sell (Direkt fusk/insättning)
            if ("eco give" in r_lower or "money give" in r_lower or "pay" in r_lower) and "joris34" in r_lower:
                # Kontrollera om han körde /sell precis innan, annars är det olagligt
                körde_sell_innan = False
                for k in range(max(0, i-3), i):
                    if "sell" in rader[k].lower() and "joris34" in rader[k].lower():
                        körde_sell_innan = True
                
                if not körde_sell_innan:
                    pengar_match = re.search(r"\d+(\.\d+)?", r_lower)
                    if pengar_match:
                        s = float(pengar_match.group())
                        total_olagliga_pengar += s
                        joris_transaktioner.append(f"OLAGLIGT: Fick ${s:.2f} direkt via kommando/insättning (Ingen /sell hittad!)")

        # =================================================================
        # DJUPANALYS: RIP_SHY (FUSKKLIENT, KOMMANDON, INJEKTIONER)
        # =================================================================
        if "rip_shy" in r_lower:
            # Hitta tidstämpel
            tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad)
            tid = tid_match.group(1) if tid_match else "00:00:00"
            ren_rad = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", rad.strip())

            # 1. Creative Mode koll
            if any(x in r_lower for x in ["gamemode c", "gamemode creative", "gm c", "gmc"]):
                rip_bevis["creative_mode"].append(f"[{tid}] Enheten gick i Creative: {ren_rad}")

            # 2. Flyg/Rörelse koll
            if "fly" in r_lower and ("enabled" in r_lower or "true" in r_lower or "issued server command" in r_lower):
                rip_bevis["fly_hacks"].append(f"[{tid}] Slog på flygläge: {ren_rad}")

            # 3. Vanilla Anti-Cheat träffar (Om servern spammar att han rör sig för snabbt = Hacked Client)
            if "moved too quickly" in r_lower or "moved wrongly" in r_lower:
                rip_bevis["vanilla_anti_cheat"].append(f"[{tid}] Servern upptäckte fuskförflyttning (Speed/Fly hack): {ren_rad}")

            # 4. Sök efter Command Abuse (Försök att köra admin-kommandon)
            if "issued server command" in r_lower:
                if any(x in r_lower for x in ["/op", "/deop", "/plugins", "/pl", "/stop", "/sk", "/luckperms", "/lp"]):
                    rip_bevis["command_abuse"].append(f"[{tid}] Försökte använda kritiskt admin-kommando: {ren_rad}")

                # 5. Sök efter Command/Script Injection (Otillåtna tecken i chatten eller kommandon)
                if any(x in r_lower for x in injection_keywords):
                    rip_bevis["script_injection"].append(f"[{tid}] MISSTÄNKT SCRIPT INJECTION (Försök att lura koden): {ren_rad}")

    # =================================================================
    # PRESENTERA DET INTENSIVA RESULTATET PÅ SKÄRMEN
    # =================================================================
    print("\n" + "=" * 70)
    print("      🔍 INTENSIV UTREDNINGS-RAPPORT FÖR SERVERN 🔍      ")
    print("=" * 70)

    # Slutsats Joris34
    print("\n[📊 JORIS34 EKONOMI-DOM]:")
    if total_olagliga_pengar > 0:
        print(f"  🔴 STATUS: OLAGLIGT! Han har tagit emot ${total_olagliga_pengar:.2f} direkt via dolda kommandon eller fusk.")
    elif total_lagliga_pengar >= 2000000:
        print(f"  🟢 STATUS: LAGLIGT MEN BUGGAT! Han tjänade ${total_lagliga_pengar:.2f} via din vanliga /sell-funktion.")
        print("            Det är inget hack, men priserna eller multiplikations-matten i ditt Skript är helt trasig.")
    elif len(joris_transaktioner) == 0:
        print("  ⚪ STATUS: Inga spår av pengatransaktioner eller miljoner hittades för Joris34 i denna fil.")
    else:
        print(f"  ⚠️ STATUS: Han har rört pengar, men inte nått upp till miljoner i denna logg. (Totalt: ${total_lagliga_pengar + total_olagliga_pengar:.2f})")

    # Visa detaljer för Joris om han gjort något
    if joris_transaktioner:
        print("  Detaljerade händelser:")
        for t in joris_transaktioner[:5]: # Visar de första 5 händelserna
            print(f"    -> {t}")
        if len(joris_transaktioner) > 5:
            print(f"    ... och {len(joris_transaktioner) - 5} till liknande rader.")

    print("-" * 70)

    # Slutsats Rip_Shy
    print("\n[⚡ RIP_SHY FUSK & HACK ANALYS]:")
    
    fusk_hittat = False
    
    if rip_bevis["script_injection"]:
        print("  🔴 [AKUT] SCRIPT INJECTION UPPTÄCKT!")
        print("     Han har försökt skriva in citattecken eller dolda LuckPerms-kommandon för att krascha/lura dina Skript.")
        for b in rip_bevis["script_injection"][:3]: print(f"      {b}")
        fusk_hittat = True

    if rip_bevis["creative_mode"]:
        print("  🔴 CREATIVE MODE UTNYTTJAT:")
        for b in rip_bevis["creative_mode"][:3]: print(f"      {b}")
        fusk_hittat = True

    if rip_bevis["fly_hacks"] or rip_bevis["vanilla_anti_cheat"]:
        print("  🔴 HACKED CLIENT / FLY / SPEED DETECTION:")
        for b in (rip_bevis["fly_hacks"] + rip_bevis["vanilla_anti_cheat"])[:3]: print(f"      {b}")
        fusk_hittat = True

    if rip_bevis["command_abuse"]:
        print("  ⚠️ OTILLÅTNA ADMIN-KOMMANDON:")
        for b in rip_bevis["command_abuse"][:3]: print(f"      {b}")
        fusk_hittat = True

    if not fusk_hittat:
        print("  🟢 Inga stenhårda spår av Fly-hacks, Creative Mode eller Script Injections hittades för Rip_Shy i just denna fil.")

    print("=" * 70 + "\n")

if __name__ == "__main__":
    super_intensiv_analys()
