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


def get(base_url, token, outdir=".", path="users", limit=100, stdout=False, ids=[], suppress_w2hdd=False):
    collected_ids = []
   
    if len(ids)==0:
        more_items_present = True 
    else:
        more_items_present = False
        collected_ids = ids
   
    # Work with paginated data
    start = 0
    while more_items_present:
        r = requests.get(
            f"{base_url}/{path}?api_token={token}&start={start}&limit={limit}"
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
        disable=stdout,
    ):
        r = requests.get(f"{base_url}/{path}/{_id}?api_token={token}").json()
        data.append(r["data"])

        if path == "files":
            try:
                f = requests.get(
                    f"{base_url}/files/{_id}/download?api_token={token}"
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
        if suppress_w2hdd==False:
            with open(os.path.join(outdir, f"{path}.json"), "w") as out_file:
                json.dump(data, out_file, indent=4, sort_keys=True)
    return data

def project_proposal_informations_from_json(data):
    d=data.pop()
    print('\\newcommand{\\cnamelong}{'+d['org_id']['name']+'\\xspace}')
    print('\\newcommand{\\caddress}{'+d['org_id']['address']+'}')
    print('\\newcommand{\\ccontactname}{'+ d['person_id']['name']+'}')
    print('\\newcommand{\\ccontactdetails}{Tel. '+d['person_id']['phone'][0]['value']+'\\\\'+d['person_id']['email'][0]['value']+'}')    
    #for i in d['person_id']['email']
    #    print(i['value'])
    #for i in d['person_id']['phone']:
    #    print(i['value'])




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



@cli.command("proposal",  help="Dump information from specific deal for a proposal")
@click.option("--token",  help="Pipedrive API token", prompt=True)
@click.option("--deal",   help="Select deal id (e.g. 64)", prompt=True)
def proposal(token, deal):
    data = get(BASE_URL, token, path="deals", limit=1, stdout=False, ids=[deal] if not isinstance(deal, list) else deal, suppress_w2hdd=True)
    project_proposal_informations_from_json(data)

def main():
    cli()


