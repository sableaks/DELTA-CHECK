import json
import os
import requests

API_KEY = os.environ.get("ROBLOX_API_KEY", "RjBUpd5EQUmCirdMQkT65G/vfwZb/6YifDNVT6xvLyNI1aPUZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaGRXUWlPaUpTYjJKc2IzaEpiblJsY201aGJDSXNJbWx6Y3lJNklrTnNiM1ZrUVhWMGFHVnVkR2xqWVhScGIyNVRaWEoyYVdObElpd2lZbUZ6WlVGd2FVdGxlU0k2SWxKcVFsVndaRFZGVVZWdFEybHlaRTFSYTFRMk5VY3ZkbVozV21Jdk5sbHBaa1JPVmxRMmVIWk1lVTVKTVdGUVZTSXNJbTkzYm1WeVNXUWlPaUl5TlRZMU9ERTBNREE1SWl3aVpYaHdJam94TnpnMU1ETXlNVEl5TENKcFlYUWlPakUzT0RVd01qZzFNaklzSW01aVppSTZNVGM0TlRBeU9EVXlNbjAuUlRLVV9ZeDVhWC10N1Nvekg5di1iVGtiZ0VkVjlKellqWjNoTGFrRlhnekJkdGpVN005Zlo4XzY2aWZWajI0X2xqcmJoanh3RlZ1cm5ibkZnNnI4SUhoN3JJUWpJSGhpNW5JczRBNnVhNGtwZ3N5bTNqSk1CUklaOTNYWGZaUkpFU0ZEbDl0VThNYWE2Z1NiVjdfZFdrbXdzTGFFTG5EMHl2QVdobmh5RHFZakxMeG14YkE4OHhRaWNfOEw3NWZUc3VRa2F6X0syWTJPYVZZOUJOMlJTT0tuaFFwOVV3dUtZSnVfb1pQd01CYUxtb1RmNXJibWhBdDR3NVJLUF9FV2VmV0F2bnlIZUh3cW1hNTFNWFIyWkZQeEliS3NBUHV2RkROOV96VHhOemVQZWk3SUU2czZCQkxWMXNPS013ZWpDelNaVENYWHhjd3BVYnZ0ZUlsVkV3").strip()

GAMES = {
    "Destroy Lucky Blocks!": "10479720091",
    "Grow a Garden 2": "10537488067",
    "Two Player Game": "10580797627",
    "Fake SAB Plaza (Pro Plaza)": "10580797627",
}

TOPIC = "commands"
COMMAND_KEY = "toilet"

def main():
    try:
        with open(os.path.join(os.environ.get("TEMP", "C:\\Temp"), "cmd_args.txt"), "r") as f:
            lines = f.read().strip().split("\n")
        game_name = lines[0]
        job_id = lines[1]
        player_name = lines[2]
        universe_id = GAMES.get(game_name, "10479720091")
        url = f"https://apis.roblox.com/messaging-service/v1/universes/{universe_id}/topics/{TOPIC}"
        payload = {"playerName": player_name, "jobId": job_id, "key": COMMAND_KEY}
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        body = {"message": json.dumps(payload)}
        requests.post(url, headers=headers, json=body, timeout=10)
    except:
        pass

if __name__ == "__main__":
    main()
