# Created By For You Babes

import asyncio
import time
import tgcrypto

from pyrogram import Client

print("""

 /\  /  _  _ |  | _ | _  _ .__.._ _  \  //  |\/|    _o _ |_)| _.   _ ._| 
/--\ \_(_)(_)|  |(/_|(/_(_||(_|| | |  \/ \_ |  ||_|_>|(_ |  |(_|\/(/_| o 
                         _|                                     /        


Github: https://github.com/lullaby23/lusiapa
""")
time.sleep(5) # Just for show off
print("Enter Your APP ID and API HASH To Generate Pyrogram String Session.")


async def main():
    async with Client(":memory:", api_id=int(input("API ID:")), api_hash=input("API HASH:")) as app:
        PYRO_SESSION = await app.export_session_string()
        await app.send_message("me", f"**Pyrogram String Session:** \n`{PYRO_SESSION}` \n\n**Powered by @Foryoubbs 😇**")
        print(f"Here is your Pyrogram String Session: \n {PYRO_SESSION} \n\nPro tip: Check Pesan Tresimpan, Backup sesion juga disimpan di pesan tersimpan :(")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
