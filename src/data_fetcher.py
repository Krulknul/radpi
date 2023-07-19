import json
import math
import os
import platform
import subprocess
import time
import requests
from kivy.clock import Clock
from grafana_client import GrafanaApi
import psycopg2
import psycopg2


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
    return f"{round(int(response['validator']['stake']['value']) / 10**18):,}"


def get_recent_uptime():
    """
    Get the recent uptime of the validator.
    """
    body = prepare_body("mainnet", VALIDATOR_ADDRESS)
    response = send_post_request("https://mainnet.clana.io/validator", body)
    uptime = float(response["validator"]["info"]["uptime"]["uptime_percentage"])
    return f"{uptime:.2f}%"


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
    data = GRAFANA.datasource.query(
        13,
        f"""info_epochmanager_currentview_view{{job="{GRAFANA_JOB}"}}""",
        time.time(),
    )
    return int(data["data"]["result"][0]["value"][1]) / 100


def get_epoch():
    """
    Get the current epoch of the validator.
    """
    job = f"""info_epochmanager_currentview_epoch{{job="{GRAFANA_JOB}"}}"""
    return f"{int(GRAFANA.datasource.query(13,job,time.time(),)['data']['result'][0]['value'][1]):,}"


def get_transactions():
    try:
        # Establish a connection to the database
        conn = psycopg2.connect(
            dbname="radix_ledger",
            user="radix",
            password="radix",
            host="db.radix.live",
            port="5432",  # default postgres port
        )

        # Create a new cursor
        cur = conn.cursor()

        # Write your query
        query = """
        SELECT accounts.address, type, (a.amount / pow(10, 18)) as amount, b.normalized_timestamp
        FROM account_xrd_stake_balance_substates a
        LEFT JOIN ledger_transactions b ON a.up_state_version = b.state_version
        LEFT JOIN accounts ON a.account_id = accounts.id
        WHERE a.validator_id = '118'
        ORDER BY a.up_state_version DESC limit 3;
        """

        # Execute the query
        cur.execute(query)

        # Fetch all rows from the last executed statement
        rows = cur.fetchall()

        # Fetch the column names from the cursor description
        col_names = [desc[0] for desc in cur.description]

        # Convert the rows into a list of dicts
        result = [dict(zip(col_names, row)) for row in reversed(rows)]

        # Close the cursor and the connection
        cur.close()
        conn.close()

        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_historic_stake():
    try:
        # Establish a connection to the database
        conn = psycopg2.connect(
            dbname="radix_ledger",
            user="radix",
            password="radix",
            host="db.radix.live",
            port="5432",  # default postgres port
        )

        # Create a new cursor
        cur = conn.cursor()

        # Write your query
        query = """
SELECT * FROM (
  SELECT
    (total_xrd_staked/pow(10, 18)) as total_xrd_staked,
    normalized_timestamp as time,
    ROW_NUMBER() OVER (ORDER BY normalized_timestamp desc) AS rownum
  FROM
    validator_stake_history
  LEFT JOIN
    ledger_transactions ON validator_stake_history.from_state_version = ledger_transactions.state_version
  WHERE
    validator_id = '118'
    AND normalized_timestamp > CURRENT_DATE - INTERVAL '30 days'
) tmp
WHERE
  tmp.rownum % 5 = 0
ORDER BY
  time DESC;
        """

        # Execute the query
        cur.execute(query)

        # Fetch all rows from the last executed statement
        rows = cur.fetchall()

        # Fetch the column names from the cursor description
        col_names = [desc[0] for desc in cur.description]

        # Convert the rows into a list of dicts
        result = [dict(zip(col_names, row)) for row in rows]

        # Close the cursor and the connection
        cur.close()
        conn.close()

        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


print(get_historic_stake())


def ping(host):
    """
    Ping the given host and return True if the host responds.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    return subprocess.call(command) == 0


def get_main_status():
    """
    Get the status of the main node.
    """
    return ping(os.environ["MAIN_IP"])


def get_backup_status():
    """
    Get the status of the backup node.
    """
    return ping(os.environ["BACKUP_IP"])
