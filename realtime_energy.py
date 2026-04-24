import asyncio
from kasa import Discover

try:
    # Newer python-kasa versions.
    from kasa import Credentials  # type: ignore
except ImportError:
    Credentials = None

try:
    # Newer python-kasa versions.
    from kasa.module import Module  # type: ignore
except ImportError:
    Module = None

IP = "10.109.133.193"
EMAIL = "janunarasimman@gmail.com"
PASSWORD = "Janu_143"
INTERVAL = 5

async def monitor():
    if Credentials:
        creds = Credentials(EMAIL, PASSWORD)
        device = await Discover.discover_single(IP, credentials=creds)
    else:
        device = await Discover.discover_single(IP)

    await device.update()

    print("Connected:", device.alias)

    while True:

        await device.update()
        if Module and hasattr(device, "modules"):
            energy = device.modules.get(Module.Energy)
            power = energy.current_consumption if energy else None
            today = energy.consumption_today if energy else None
            month = energy.consumption_this_month if energy else None
            total = energy.consumption_total if energy else None
        else:
            realtime = getattr(device, "emeter_realtime", {}) or {}
            power = realtime.get("power")
            if power is None and realtime.get("power_mw") is not None:
                power = realtime["power_mw"] / 1000
            today = getattr(device, "emeter_today", None)
            month = getattr(device, "emeter_this_month", None)
            total = getattr(device, "emeter_total", None)

        print("Power:", round(power, 2) if power is not None else "N/A", "W")
        print("Energy Today:", today, "kWh")
        print("Energy Month:", month, "kWh")
        print("Energy Total:", total, "kWh")
        print("----------------------------")

        await asyncio.sleep(INTERVAL)

asyncio.run(monitor())
