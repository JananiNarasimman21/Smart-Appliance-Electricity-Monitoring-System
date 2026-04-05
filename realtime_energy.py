import asyncio
from kasa import Discover, Credentials
from kasa.module import Module

IP = "10.109.133.193"
EMAIL = "janunarasimman@gmail.com"
PASSWORD = "Janu_143"
INTERVAL = 5

async def monitor():

    creds = Credentials(EMAIL, PASSWORD)

    device = await Discover.discover_single(IP, credentials=creds)

    await device.update()

    print("Connected:", device.alias)

    energy = device.modules.get(Module.Energy)

    while True:

        await device.update()

        power = energy.current_consumption
        today = energy.consumption_today
        month = energy.consumption_this_month
        total = energy.consumption_total

        print("Power:", round(power,2), "W")
        print("Energy Today:", today, "kWh")
        print("Energy Month:", month, "kWh")
        print("Energy Total:", total, "kWh")
        print("----------------------------")

        await asyncio.sleep(INTERVAL)

asyncio.run(monitor())