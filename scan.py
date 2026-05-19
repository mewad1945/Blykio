import re
import os

LOG_FILE_PATH = "latest.log"

def skriv_ut_tabell_linje(bredder):
    print("+" + "+".join(["-" * (w + 2) for w in bredder]) + "+")

def skriv_ut_rad(data, bredder):
    formaterad_data = [str(item)[:w].ljust(w) for item, w in zip(data, bredder)]
    print("| " + " | ".join(formaterad_data) + " |")

def skanna_server_logg():
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Hittade inte loggfilen: {LOG_FILE_PATH}.")
        return

    rip_shy_events = []
    joris_events = []
    
    # Sökord för Rip_Shy (fokus på fly, creative, gm, op, fly-hacks)
    rip_keywords = ["fly", "gamemode", "gm", "creative", "op", "deop", "permission", "setblock"]
    
    # Sökord för Joris34 (fokus på ekonomi, din hemmasnickrade /sell, worth och eco give)
    joris_keywords = ["sell", "shop", "worth", "eco", "give", "money", "balance", "vault"]

    print("\n" + "=" * 80)
    print(" LÄSER IN LOGGFIL OCH ANALYSERAR TIDSLINJEN... ".center(80, "="))
    print("=" * 80 + "\n")

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as file:
        rader = file.readlines()

    for i, rad in enumerate(rader):
        rad_clean = rad.strip()
        
        # Extrahera tidstämpel om den finns (t.ex. [13:09:29])
        tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", rad_clean)
        tid = tid_match.group(1) if tid_match else "Okänd tid"
        
        # Ta bort tid och info-taggar för renare text i tabellen
        ren_text = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", rad_clean)

        # -------------------------------------------------------------
        # 1. SPÅRA RIP_SHY (Kommandon, Fly, Creative, fusktendenser)
        # -------------------------------------------------------------
        if "rip_shy" in rad_clean.lower():
            event_typ = "Kommando"
            if any(k in rad_clean.lower() for k in ["op", "permission"]):
                event_typ = "Behörighet"
            elif any(k in rad_clean.lower() for k in ["creative", "gamemode", "gm"]):
                event_typ = "Spelläge"
            elif "fly" in rad_clean.lower():
                event_typ = "Flyg/Rörelse"
                
            rip_shy_events.append([tid, event_typ, ren_text])
            
        # Spara även om konsolen ändrar något på Rip_Shy utan att hans namn står som utförare
        elif "rip_shy" in rad_clean.lower() and "issued server command" not in rad_clean.lower():
            if any(k in rad_clean.lower() for k in rip_keywords):
                rip_shy_events.append([tid, "Konsol/System", ren_text])

        # -------------------------------------------------------------
        # 2. SPÅRA JORIS34 & DIN SPECIELLA /SELL (Worth + Eco Give)
        # -------------------------------------------------------------
        if "joris34" in rad_clean.lower():
            event_typ = "Spelare Aktiv"
            if "sell" in rad_clean.lower() or "shop" in rad_clean.lower():
                event_typ = "Öppnade Shop/Sell"
            elif "worth" in rad_clean.lower():
                event_typ = "Kollade Värde"
                
            joris_events.append([tid, event_typ, ren_text])
            
            # KOLLA RADERNA PRECIS EFTER (Tidslinje-analys för dolda konsolkommandon!)
            # Om ditt GUI kör "worth" och sedan "eco give" sekunden efter:
            for j in range(1, 4): # Kollar upp till 3 rader efter Joris handling
                if i + j < len(rader):
                    nasta_rad = rader[i + j].strip()
                    nasta_tid_match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", nasta_rad)
                    nasta_tid = nasta_tid_match.group(1) if nasta_tid_match else tid
                    nasta_ren = re.sub(r"^\[\d{2}:\d{2}:\d{2}\s+\w+\]:\s*", "", nasta_rad)
                    
                    if "eco" in nasta_rad.lower() or "give" in nasta_rad.lower() or "worth" in nasta_rad.lower():
                        if nasta_ren not in [e[2] for e in joris_events]: # Undvik dubbletter
                            joris_events.append([nasta_tid, "Kopplat Konsol-Kommando", f"[Triggad av Joris] {nasta_ren}"])

        # Fånga upp lösa "eco give" eller "worth" i loggen som kan ha missats
        elif any(x in rad_clean.lower() for x in ["eco give", "worth"]) and "2000000" in rad_clean.lower():
            joris_events.append([tid, "Oidentifierad Miljonaffär", ren_text])

    # -------------------------------------------------------------
    # SKRIV UT TABELLERNA
    # -------------------------------------------------------------
    
    # TABELL 1: RIP_SHY
    print(" TABELL: RIP_SHY - MISSTÄNKTA KOMMANDON / FLY / CREATIVE ")
    bredder_rip = [10, 15, 85]
    skriv_ut_tabell_linje(bredder_rip)
    skriv_ut_rad(["TID", "HÄNDELSE", "LOGG-TEXT (VAD SOM HÄNDE)"], bredder_rip)
    skriv_ut_tabell_linje(bredder_rip)
    if rip_shy_events:
        for ev in rip_shy_events:
            skriv_ut_rad(ev, bredder_rip)
    else:
        skriv_ut_rad(["-", "Inga fynd", "Hittade inga misstänkta rader för Rip_Shy."], bredder_rip)
    skriv_ut_tabell_linje(bredder_rip)

    print("\n\n" + "="*120 + "\n\n")

    # TABELL 2: JORIS34
    print(" TABELL: JORIS34 - EKONOMI / /SELL / WORTH / ECO GIVE ")
    bredder_joris = [10, 25, 75]
    skriv_ut_tabell_linje(bredder_joris)
    skriv_ut_rad(["TID", "KATEGORI", "DETALJER (SE OM DET STÅR WORTH / ECO GIVE)"], bredder_joris)
    skriv_ut_tabell_linje(bredder_joris)
    if joris_events:
        # Sortera efter tid så tidslinjen blir helt perfekt
        joris_events.sort(key=lambda x: x[0])
        for ev in joris_events:
            skriv_ut_rad(ev, bredder_joris)
    else:
        skriv_ut_rad(["-", "Inga fynd", "Hittade inga ekonomiska loggar för Joris34."], bredder_joris)
    skriv_ut_tabell_linje(bredder_joris)

if __name__ == "__main__":
    skanna_server_logg()
