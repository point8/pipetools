import os
import json
import tqdm
import time
import click
import random
import requests

from requests.exceptions import ConnectionError

BASE_URL = "https://api.pipedrive.com/v1"
TOPICS = [
    "users",
    "deals",
    "persons",
    "organizations",
    "pipelines",
    "stages",
    "files",
    "activities",
]


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get(base_url, token, outdir=".", path="users", sub_path="", limit=100, stdout=False, ids=[], params={}, silent=False):
    collected_ids = []

    if len(ids)==0:
        more_items_present = True
    else:
        more_items_present = False
        collected_ids = ids

    # if params:
    #     params = "&" + "&".join(params)
    # else:
    #     params = ""

    if sub_path != "":
        sub_path = "/" + sub_path


    # Work with paginated data
    start = 0
    while more_items_present:
        payload = params.copy()
        payload['api_token'] = token
        payload['start'] = start
        payload['limit'] = limit
        r = requests.get(
            f"{base_url}/{path}", params=payload
        ).json()
        try:
            more_items_present = r["additional_data"]["pagination"][
                "more_items_in_collection"
            ]
        except:
            more_items_present = False
        collected_ids = collected_ids + [entry["id"] for entry in r["data"]]
        start += limit

    collected_ids = list(set(collected_ids))

    data = []
    n_connection_errors = 0
    for _id in tqdm.tqdm(
        collected_ids,
        ncols=120,
        unit="entry",
        desc=f"Load data for path: /{path}",
        disable=stdout or silent,
    ):
        payload = params.copy()
        payload['api_token'] = token
        r = requests.get(f"{base_url}/{path}/{_id}{sub_path}", params=payload).json()
        data.append(r["data"])

        if path == "files":
            try:
                f = requests.get(
                    f"{base_url}/files/{_id}/download?api_token={token}{params}"
                )
                with open(
                    os.path.join(os.path.join(outdir, "files"), r["data"]["name"]),
                    "wb",
                ) as out_file:
                    out_file.write(f.content)
            except ConnectionError as err:
                # print('ERROR:', err)
                n_connection_errors += 1
            time.sleep(random.random() / 10)  # Random throttling of file download

    if path == "files":
        tqdm.tqdm.write(f"Catched {n_connection_errors} connection errors")

    if stdout:
        print(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))
    else:
        with open(os.path.join(outdir, f"{path}.json"), "w") as out_file:
            json.dump(data, out_file, indent=4, sort_keys=True)
    return data


@click.group(help="Command line tools for Pipedrive CRM")
def cli():
    pass


@cli.command("backup", help="Run Pipedrive CRM data backup")
@click.argument("outdir", default=".")
@click.option("--token", help="Pipedrive CRM API token", prompt=True)
@click.option("--topic", help="Select topic", type=click.Choice(TOPICS))
@click.option("--stdout", help="Output to stdout instead of file", is_flag=True)
def backup(outdir, token, topic, stdout):
    if not stdout:
        print(f"Saving backup data to {outdir}")
    mkdir(outdir)

    if topic is not None:
        topics = [topic]
    else:
        topics = TOPICS

    if "files" in topics:
        mkdir(os.path.join(outdir, "files"))

    for topic in tqdm.tqdm(
        topics,
        ncols=120,
        unit="topic",
        desc="Request data for topics",
        leave=False,
        disable=stdout,
    ):
        get(BASE_URL, token, outdir, path=topic, limit=250, stdout=stdout)



@cli.command("deal",      help="Fetch deal as JSON with DEALID (e.g. 42)")
@click.argument("dealid")
@click.option("--outdir", help="Set directory to save JSON file", default=".")
@click.option("--token",  help="Pipedrive CRE API token", prompt=True)
@click.option("--stdout", help="Output to stdout instead of file", is_flag=True)
def deal(outdir, token, dealid, stdout):
    if not stdout:
        print(f"Saving JSON deal data to {outdir}")
    mkdir(outdir)
    data = get(BASE_URL, token, path="deals", limit=1, stdout=stdout, ids=[dealid] if not isinstance(dealid, list) else dealid)

@cli.command("stats", help="Fetch sales statistics (WIP)")
@click.option("--token",  help="Pipedrive CRE API token", prompt=True)
@click.option("--stdout", help="Output to stdout instead of file", is_flag=True)
@click.option("--outdir", help="Set directory to save JSON file", default=".")
def stats(token, stdout, outdir):
    if not stdout:
        print(f"Saving JSON deal data to {outdir}")
    mkdir(outdir)

    r = requests.get(
        f"{BASE_URL}/deals/timeline?start_date=2019-01-01&interval=month&amount=12&field_key=won_time&pipeline_id=2&filter_id=2&api_token={token}"
    ).json()
    monthly_stats = []
    for period in r["data"]:
        monthly_stats.append({
                "start": period["period_start"],
                "end": period["period_end"],
                "count": period["totals"]["count"],
                "value": period["totals"]["values"]
            })
    if stdout:
        print(json.dumps(monthly_stats, indent=4, sort_keys=True, ensure_ascii=False))
    else:
        with open(os.path.join(outdir, f"stats.json"), "w") as out_file:
            json.dump(monthly_stats, out_file, indent=4, sort_keys=True)

def main():
    cli()

