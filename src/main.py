# main.py
import ujson
from app.lib.ota_update.ota_updater import OTAUpdater
from app.esp_game_of_life import App


def download_and_install_update_if_available(config):
    if 'wifi' in config:
        o = OTAUpdater('https://github.com/scoggins/esp_game_of_life')
        o.download_and_install_update_if_available(config['wifi']['ssid'], config['wifi']['password'])
    else:
        print('No WIFI configured, skipping updates check')

def main():
    with open('config.json') as cfg:
        config = ujson.load(cfg)

    download_and_install_update_if_available(config)
    App(config)

if __name__ == "__main__":
    main()

