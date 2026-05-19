import os

LOG_FILE_PATH = "latest.log"

def intensiv_skanning():
    if not os.path.exists(LOG_FILE_PATH):
        print("Hittade inte latest.log! Lägg skriptet i rätt mapp.")
        return

    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        rader = f.readlines()

    # Variabler för att samla stenhårda bevis
    joris_sell_count = 0
    joris_received_from_rip = False
    joris_illegal_eco = False
    
    rip_gmc = False
    rip_fly = False
    rip_script_injection = False

    # Loopa igenom HELA loggen rad för rad
    for i, rad in enumerate(rader):
        r_lower = rad.lower()

        # --- JORIS34 DJUPANALYS ---
        if "joris34" in r_lower:
            if "sell" in r_lower:
                joris_sell_count += 1
            if "pay" in r_lower and "rip_shy" in r_lower:
                joris_received_from_rip = True
            if "eco give" in r_lower or "money give" in r_lower:
                # Kolla om det fanns en /sell-handling precis innan
                gick_via_sell = False
                for j in range(max(0, i-3), i):
                    if "sell" in rader[j].lower():
                        gick_via_sell = True
                if not gick_via_sell:
                    joris_illegal_eco = True

        # --- RIP_SHY DJUPANALYS ---
        if "rip_shy" in r_lower:
            if any(x in r_lower for x in ["gamemode c", "gamemode creative", "gm c", "gmc"]):
                rip_gmc = True
            if "fly" in r_lower:
                rip_fly = True
            # Letar efter tecken på Script Injection (konstiga kommandoförsök)
            if "issued server command" in r_lower:
                if any(x in r_lower for x in ["\"", "'", "&&", "eval", "skript", "parent set"]):
                    rip_script_injection = True

    print("\n" + "=" * 60)
    print("      INTENSIV ANALYS KLART – HÄR ÄR SVARET:")
    print("=" * 60)

    # SLUTSATS: JORIS34
    if joris_received_from_rip:
        print("[JORIS34]: OLAGLIGT. Han tog emot pengarna direkt från fuskaren Rip_Shy via /pay.")
    elif joris_illegal_eco:
        print("[JORIS34]: OLAGLIGT. Någon (eller ett hack) körde /eco give på honom utan att han sålde något.")
    elif joris_sell_count > 0:
        print(f"[JORIS34]: LAGLIGT MEN BUGGAT. Han använde din /sell {joris_sell_count} gånger. Priserna i ditt sälj-GUI är felinställda!")
    else:
        print("[JORIS34]: INGA SPÅR. Hittade inga miljonaffärer alls kopplade till honom i denna fil.")

    # SLUTSATS: RIP_SHY
    if rip_gmc and rip_fly:
        print("[RIP_SHY]: FUSKADE. Tog sig in i Creative Mode OCH slog på Fly.")
    elif rip_gmc:
        print("[RIP_SHY]: FUSKADE. Gick in i Creative Mode (/gamemode c).")
    elif rip_fly:
        print("[RIP_SHY]: FUSKADE. Slog på flyg-läge.")
    else:
        print("[RIP_SHY]: Inga spår av Creative/Fly.")

    # SLUTSATS: SCRIPT INJECTION / HACK METOD
    if rip_script_injection:
        print("[METOD]: SCRIPT INJECTION. Rip_Shy försökte lura dina Skript att köra konsolkommandon!")
    elif joris_illegal_eco or rip_gmc:
        print("[METOD]: OP-LÄCKA. De har troligen lyckats få OP-rättigheter eller stulit stjärn-permission (*).")
    else:
        print("[METOD]: Inga tecken på systemhack. Det rör sig troligen om felinställda priser i ditt sälj-GUI.")

    print("=" * 60 + "\n")

if __name__ == "__main__":
    intensiv_skanning()
