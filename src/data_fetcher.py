import asyncio
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
import aiohttp
import asyncpg


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


async def send_post_request(url, body):
    """
    Send a POST request to the given URL with the provided body and return the response.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body) as response:
            return await response.json()


async def get_stake():
    """
    Get the stake of the validator.
    """
    body = prepare_body("mainnet", VALIDATOR_ADDRESS)
    response = await send_post_request("https://mainnet.clana.io/validator", body)
    return f"{round(int(response['validator']['stake']['value']) / 10**18):,}"


async def get_recent_uptime():
    """
    Get the recent uptime of the validator.
    """
    body = prepare_body("mainnet", VALIDATOR_ADDRESS)
    response = await send_post_request("https://mainnet.clana.io/validator", body)
    uptime = float(response["validator"]["info"]["uptime"]["uptime_percentage"])
    return f"{uptime:.2f}%"


async def get_rank():
    """
    Get the rank of the validator.
    """
    body = prepare_body("mainnet")
    response = await send_post_request("https://mainnet.clana.io/validators", body)

    for i, validator in enumerate(response["validators"]):
        if validator["validator_identifier"]["address"] == VALIDATOR_ADDRESS:
            return i + 1
    return None


async def get_proposal_data():
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


async def get_activity_data():
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


async def get_epoch_progress():
    """
    Get the epoch progress of the validator.
    """
    data = GRAFANA.datasource.query(
        13,
        f"""info_epochmanager_currentview_view{{job="{GRAFANA_JOB}"}}""",
        time.time(),
    )
    print(data)
    result = int(data["data"]["result"][0]["value"][1]) / 100
    print(result)
    return result


async def get_epoch():
    """
    Get the current epoch of the validator.
    """
    job = f"""info_epochmanager_currentview_epoch{{job="{GRAFANA_JOB}"}}"""
    data = GRAFANA.datasource.query(13, job, time.time())
    data = data["data"]["result"][0]["value"][1]
    return f"{int(data):,}"


async def get_sql_data(query):
    try:
        # Establish a connection to the database
        conn = await asyncpg.connect(
            database="radix_ledger",
            user="radix",
            password="radix",
            host="db.radix.live",
            port="5432",  # default postgres port
        )

        # Fetch all rows from the last executed statement
        rows = await conn.fetch(query)

        # Fetch the column names from the cursor description
        col_names = [desc for desc in rows[0].keys()]

        # Convert the rows into a list of dicts
        result = [dict(zip(col_names, row)) for row in reversed(rows)]

        # Close the connection
        await conn.close()

        return result
    except Exception as error:
        print(error)


async def get_transactions():
    # Write your query
    query = """
        SELECT accounts.address, type, (a.amount / pow(10, 18)) as amount, b.normalized_timestamp
        FROM account_xrd_stake_balance_substates a
        LEFT JOIN ledger_transactions b ON a.up_state_version = b.state_version
        LEFT JOIN accounts ON a.account_id = accounts.id
        WHERE a.validator_id = '118'
        ORDER BY a.up_state_version DESC limit 3;
        """
    return await get_sql_data(query)


async def printer():
    print(await get_transactions())


asyncio.get_event_loop().run_until_complete(printer())


async def get_historic_stake_month():
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
  tmp.rownum % 5 = 0 OR tmp.rownum = 1
ORDER BY
  time DESC;
        """
    return await get_sql_data(query)


async def get_historic_stake_week():
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
    AND normalized_timestamp > CURRENT_DATE - INTERVAL '7 days'
) tmp
WHERE
  tmp.rownum % 5 = 0
ORDER BY
  time DESC;
        """
    return await get_sql_data(query)


async def ping(host):
    """
    Ping the given host and return True if the host responds.
    """
    process = await asyncio.create_subprocess_shell(
        f"ping -c 1 {host}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return process.returncode == 0


async def get_main_status():
    """
    Get the status of the main node.
    """
    return await ping(os.environ["MAIN_IP"])


async def get_backup_status():
    """
    Get the status of the backup node.
    """
    return await ping(os.environ["BACKUP_IP"])
