# main.py
import ujson
from app.lib.ota_update.ota_updater import OTAUpdater
from app.esp_game_of_life import App


def download_and_install_update_if_available(config):
    if 'wifi' in config:
        o = OTAUpdater(github_repo=config['github']['repo'],
                       github_src_dir=config['github']['src_dir'],
                       main_dir=config['github']['main_dir']
        )
        o.install_update_if_available_after_boot(config['wifi']['ssid'], config['wifi']['password'])
    else:
        print('No WIFI configured, skipping updates check')

def main():
    with open('config.json') as cfg:
        config = ujson.load(cfg)

    download_and_install_update_if_available(config)
    App(config)

if __name__ == "__main__":
    main()

