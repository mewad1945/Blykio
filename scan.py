import re
import os

# Ange namnet på din loggfil (oftast latest.log i mappen "logs")
LOG_FILE_PATH = "latest.log" 

def skanna_server_logg():
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Hittade inte loggfilen: {LOG_FILE_PATH}. Lägg skriptet i samma mapp som loggen eller ändra sökvägen.")
        return

    print("=" * 60)
    print(" SÖKER EFTER MISSTÄNKT AKTIVITET PÅ SERVERN ")
    print("=" * 60)

    # Listor för att spara träffar
    rip_shy_activity = []
    joris_money_activity = []

    # Regex/sökord för kommandon som Rip_Shy kan ha kört
    misstankta_kommandon = [r"/pay", r"/sell", r"/fly", r"/gamemode", r"/gm"]

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as file:
        for rad in file:
            # 1. KOLLA RIP_SHY
            if "Rip_Shy" in rad or "rip_shy" in rad.lower():
                # Kolla om raden innehåller något av de misstänkta kommandona
                for cmd in misstankta_kommandon:
                    if re.search(cmd, rad, re.IGNORECASE):
                        rip_shy_activity.append(rad.strip())
                        break # Hittat ett kommando på denna rad, gå till nästa
                
                # Spara även om han blev OP eller fick permissions mitt i allt
                if "op " in rad.lower() or "permission" in rad.lower():
                    rip_shy_activity.append(f"[BEHÖRIGHET] {rad.strip()}")

            # 2. KOLLA JORIS34, PENGAR OCH SÄLJ-KOMMANDON
            if "Joris34" in rad or "joris34" in rad.lower():
                # NYTT: Söker efter pengar, eco-kommandon, men NU ÄVEN /sell och /shop!
                if any(x in rad.lower() for x in ["eco", "give", "money", "pay", "balance", "add", "set", "2000000", "sell", "shop"]):
                    joris_money_activity.append(rad.strip())

    # --- PRESENTERA RESULTATET ---
    
    print(f"\n[+] RAPPORT FÖR Rip_Shy ({len(rip_shy_activity)} misstänkta händelser hittade):")
    if rip_shy_activity:
        for händelse in rip_shy_activity:
            print(f"  -> {händelse}")
    else:
        print("  Inga specifika /pay, /sell, /fly eller /gamemode hittades för Rip_Shy i denna fil.")

    print("\n" + "="*60)

    print(f"\n[+] RAPPORT FÖR Joris34 (Pengar, /sell & /shop - {len(joris_money_activity)} händelser hittade):")
    if joris_money_activity:
        for händelse in joris_money_activity:
            print(f"  -> {händelse}")
    else:
        print("  Hittade inga penga- eller säljkommandon kopplade till Joris34 i loggen.")
        print("  TIPS: Om pengarna kom från en buggig admin-shop kan det hända att EssentialsX/ShopGUI+ loggar det i en egen separat loggfil i plugin-mappen.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    skanna_server_logg()
