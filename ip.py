import os
import re

def skanna_proxy_loggar():
    # Sök efter alla filer som börjar med proxy.log
    logg_filer = [f for f in os.listdir('.') if f.startswith('proxy.log')]
    
    if not logg_filer:
        print("❌ Hittade inga proxy.log-filer i denna mapp!")
        print("Se till att du kör skriptet inuti mappen: /root/eagler-network/proxy")
        return

    print("\n" + "=" * 70)
    print("🌐    EAGLER-PROXY IP-DETEKTIV: SÖKER EFTER ANMÄLDA SPELARE    🌐")
    print("=" * 70)

    mål_spelare = ["rip_shy", "joris34"]
    hittade_resultat = False

    # Regex för att fånga IP-adresser (både vanliga IPv4 och IPv6/bungee format)
    ip_pattern = r"(/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"

    for fil_namn in sorted(logg_filer):
        print(f"🔍 Skannar fil: {fil_namn}...")
        
        try:
            with open(fil_namn, "r", encoding="utf-8", errors="ignore") as f:
                for rad_nummer, rad in enumerate(f, 1):
                    rad_lower = rad.lower()
                    
                    # Kolla om någon av spelarna finns på raden
                    for spelare in mål_spelare:
                        if spelare in rad_lower:
                            # Försök plocka ut IP-adressen från raden
                            ip_match = re.search(ip_pattern, rad)
                            ip_adress = "Okänd IP (Kunde inte extrahera)"
                            
                            if ip_match:
                                # Välj den rena IP-träffen utan snedstreck eller portar
                                ip_adress = ip_match.group(2) if ip_match.group(2) else ip_match.group(3)

                            print(f"  📌 HITTAI INLOGGNING i {fil_namn} (Rad {rad_nummer}):")
                            print(f"     👤 Spelare: {spelare.upper()}")
                            print(f"     🌐 IP-Adress: {ip_adress}")
                            print(f"     📄 Loggrad: {rad.strip()}\n")
                            hittade_resultat = True
                            
        except Exception as e:
            print(f"⚠️ Kunde inte läsa {fil_namn}: {e}")

    print("=" * 70)
    if not hittade_resultat:
        print("⚪ Inga spår av IP-adresser för Rip_Shy eller Joris34 hittades i proxy-loggarna.")
    else:
        print("✅ Skanning klar. Använd IP-adresserna ovan för att lägga till i din Bungee/Waterfall ban-lista!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    skanna_proxy_loggar()
