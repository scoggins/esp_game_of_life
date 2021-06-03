# main.py
import ujson
import machine
from app.utils.ota_update.ota_updater import OTAUpdater
from app.esp_game_of_life import App


def download_and_install_update_if_available(config):
    if 'wifi' in config:
        o = OTAUpdater(github_repo=config['github']['repo'],
                       github_src_dir=config['github']['src_dir'],
                       main_dir=config['github']['main_dir']
        )
        OTAUpdater._using_network(config['wifi']['ssid'], config['wifi']['password'])
        if o.install_update_if_available():
            machine.reset()
    else:
        print('No WIFI configured, skipping updates check')

def main():
    global app
    with open('config.json') as cfg:
        config = ujson.load(cfg)

    download_and_install_update_if_available(config)
    app = App(config)
    app.start()

if __name__ == "__main__":
    main()

app = None
