import json
import math
import os
import platform
import subprocess
import time
import requests
from kivy.clock import Clock
from grafana_client import GrafanaApi

# Set up environment variables
GRAFANA_URL = os.environ["GRAFANA_URL"]
VALIDATOR_ADDRESS = os.environ["VALIDATOR_ADDRESS"]
GRAFANA_JOB = os.environ["GRAFANA_JOB"]

# Set up Grafana API
GRAFANA = GrafanaApi.from_url(
    GRAFANA_URL,
    credential=os.environ["GRAFANA_TOKEN"],
)


def prepare_body(network, address=None):
    """
    Prepare the body for POST request.
    """
    body = {
        "network_identifier": {"network": network},
    }

    if address:
        body["validator_identifier"] = {"address": address}

    return body


def send_post_request(url, body):
    """
    Send a POST request to the given URL with the provided body and return the response.
    """
    response = requests.post(url, json=body)
    return response.json()


def get_stake():
    """
    Get the stake of the validator.
    """
    body = prepare_body("mainnet", VALIDATOR_ADDRESS)
    response = send_post_request("https://mainnet.clana.io/validator", body)
    return round(int(response["validator"]["stake"]["value"]) / 10**18)


def get_recent_uptime():
    """
    Get the recent uptime of the validator.
    """
    body = prepare_body("mainnet", VALIDATOR_ADDRESS)
    response = send_post_request("https://mainnet.clana.io/validator", body)
    return float(response["validator"]["info"]["uptime"]["uptime_percentage"])


def get_rank():
    """
    Get the rank of the validator.
    """
    body = prepare_body("mainnet")
    response = send_post_request("https://mainnet.clana.io/validators", body)

    for i, validator in enumerate(response["validators"]):
        if validator["validator_identifier"]["address"] == VALIDATOR_ADDRESS:
            return i + 1
    return None


def get_proposal_data():
    """
    Get the proposal data of the validator.
    """
    return GRAFANA.datasource.query_range(
        13,
        f"""info_counters_radix_engine_cur_epoch_completed_proposals{{job="{GRAFANA_JOB}"}}""",
        time.time() - 60 * 60 * 3,
        time.time(),
        "1m",
    )


def get_activity_data():
    """
    Get the activity data of the validator.
    """
    current_time = (
        math.floor(time.time() / 3600) * 3600
    )  # Round current time to nearest whole hour

    start_time = current_time - 24 * 3600  # Subtract 24 hours to get the start time
    end_time = current_time

    return GRAFANA.datasource.query_range(
        13,
        f"""increase(info_counters_radix_engine_user_transactions{{job="{GRAFANA_JOB}"}}[1h])""",
        start_time,
        end_time,
        "1h",
    )


def get_epoch_progress():
    """
    Get the epoch progress of the validator.
    """
    return GRAFANA.datasource.query(
        13,
        f"""info_epochmanager_currentview_view{{job="{GRAFANA_JOB}"}}""",
        time.time(),
    )


def get_epoch():
    """
    Get the current epoch of the validator.
    """
    return GRAFANA.datasource.query(
        13,
        f"""info_epochmanager_currentview_epoch{{job="{GRAFANA_JOB}"}}""",
        time.time(),
    )["data"]["result"][0]["value"][1]


def ping(host):
    """
    Ping the given host and return True if the host responds.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    return subprocess.call(command) == 0


def data_fetcher(app):
    """
    Continuously fetch and update data for the app.
    """
    while True:
        try:
            proposal_data = get_proposal_data()
            progress_data = get_epoch_progress()
            activity_data = get_activity_data()
            epoch = int(get_epoch())
            stake = get_stake()
            rank = get_rank()
            uptime = get_recent_uptime()
            main_status = ping(os.environ["MAIN_IP"])
            backup_status = ping(os.environ["BACKUP_IP"])

            # Schedule the app updates
            Clock.schedule_once(lambda dt: app.update_proposal_graph(proposal_data))
            Clock.schedule_once(lambda dt: app.update_progress(progress_data))
            Clock.schedule_once(lambda dt: app.update_activity_graph(activity_data))
            Clock.schedule_once(lambda dt: app.values.set_epoch(epoch))
            Clock.schedule_once(lambda dt: app.values.set_stake(stake))
            Clock.schedule_once(lambda dt: app.values.set_rank(rank))
            Clock.schedule_once(lambda dt: app.values.set_uptime(uptime))
            Clock.schedule_once(lambda dt: app.values.set_main(main_status))
            Clock.schedule_once(lambda dt: app.values.set_backup(backup_status))
        except Exception as e:
            print(e)
            continue

        # This is some code for initiating alert mode and playing a sound.
        # It is disabled, as I could not figure out how to play sounds through the audio jack on the raspberry pi.
        # the sound does play when testing on my laptop.
        # Clock.schedule_once(lambda dt: app.start_alert_mode())

        # filename = "alert.mp3"

        # # Create a VLC media player instance
        # player = vlc.MediaPlayer()

        # # Load the file into the media player
        # media = vlc.Media(filename)
        # player.set_media(media)

        # # Play the sound
        # player.play()

        # # Wait for the sound to finish playing
        # while player.is_playing():
        #     pass

        time.sleep(5)
