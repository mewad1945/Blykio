import time
import random
import requests

def gen(length):
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def main():
    print("Python runtime ready")
    print("Started scanning (6-digit pins)...")
    
    url = "https://blooket.com"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://blooket.com",
        "Referer": "https://blooket.com/",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    session.headers.update(headers)

    while True:
        gen_num = gen(6)
        payload = {"id": gen_num}
        
        try:
            response = session.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"[+] Hittade ett aktivt spel: {gen_num}")
            else:
                # Skriver ut exakt vilken statuskod servern svarar med (t.ex. 403 vid blockering)
                print(f"[!] Servern svarade med statuskod: {response.status_code} för kod {gen_num}")
                if response.status_code == 403:
                    print("    -> 403 betyder oftast att Cloudflare/Blooket blockerar din IP-adress.")
                elif response.status_code == 429:
                    print("    -> 429 betyder Rate Limit (för många anrop). Väntar 15 sekunder...")
                    time.sleep(15)
            
            time.sleep(0.5)
                    
        except requests.exceptions.RequestException as e:
            # Skriver ut det exakta tekniska felet (t.ex. ConnectionError eller Timeout)
            print(f"\n[X] NÄTVERKSFEL: {type(e).__name__}")
            print(f"    Detaljer: {e}")
            print("    Väntar 5 sekunder innan nästa försök...\n")
            time.sleep(5)

if __name__ == "__main__":
    main()
