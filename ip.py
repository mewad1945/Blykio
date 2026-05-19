import re
import os

# Mappen där proxy-loggarna ligger
log_dir = "/root/eagler-network/proxy/"
target_player = "Rip_Shy"

def get_player_ip():
    # Regex för att hitta IP-adresser i loggen (exkluderar port)
    ip_pattern = r"/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):"
    
    # Gå igenom alla filer som börjar med proxy.log
    for filename in os.listdir(log_dir):
        if filename.startswith("proxy.log"):
            filepath = os.path.join(log_dir, filename)
            with open(filepath, 'r', errors='ignore') as file:
                for line in file:
                    if target_player in line:
                        match = re.search(ip_pattern, line)
                        if match:
                            ip = match.group(1)
                            print(f"IP för {target_player}: {ip}")
                            return # Avsluta efter första hittade IPn

get_player_ip()
