import GameSenseManager
import pystray
import PIL.Image
import threading

def battery_checker():
    mouse_prime.startApp()


def tray():
    def onClick(icon, item):
        if str(item) == "Exit":
            mouse_prime.exitApp()
            mouse_prime.removeApp()
            icon.stop()


    logo = PIL.Image.open("logo.png")
    icon = pystray.Icon("battery", logo,"Mouse Battery Idicator for OLED", menu=pystray.Menu(
        pystray.MenuItem("Exit", onClick)
    ))

    threading.Thread(target=battery_checker, daemon=True).start()
    icon.run()


mouse_prime = GameSenseManager.GameSenseManager()
mouse_prime.addAppToSSE()
tray()

