import os
import json
import tqdm
import click
import requests


BASE_URL = 'https://api.pipedrive.com/v1'


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get(base_url, token, outdir, path='users', limit=100):
    collected_ids = []
    
    # Work with paginated data
    more_items_present = True
    start = 0
    while more_items_present:
        r = requests.get(f'{base_url}/{path}?api_token={token}&start={start}&limit={limit}').json()
        try:
            more_items_present = r['additional_data']['pagination']['more_items_in_collection']
        except:
            more_items_present = False
        collected_ids = collected_ids + [entry['id'] for entry in r['data']]
        start += limit

    collected_ids = list(set(collected_ids))

    data = []
    for _id in tqdm.tqdm(collected_ids, ncols=120, unit='entries', desc=f'Load data for path: /{path}'):
        r = requests.get(f'{base_url}/{path}/{_id}?api_token={token}').json()
        data.append(r['data'])

        if path == 'files':
            f = requests.get(f'{base_url}/files/{_id}/download?api_token={token}')
            with open(os.path.join(os.path.join(outdir, 'files'), r['data']['name']), 'wb') as out_file:
                out_file.write(f.content)

    with open(os.path.join(outdir, f'{path}.json'), 'w') as out_file:
        json.dump(data, out_file, indent=4, sort_keys=True)


@click.group(help='Command line tools for Pipedrive CRM')
def cli():
    pass


@cli.command('backup', help='Run Pipedrive CRM data backup')
@click.argument('outdir', default='.')
@click.option('--token', help='Pipedrive CRM API token', prompt=True)
def backup(outdir, token):
    print(f'Saving backup data to {outdir}')
    mkdir(outdir)
    topics = ['users', 'deals', 'persons', 'organizations', 'pipelines', 'stages', 'files', 'activities', 'notes']
    if 'files' in topics:
        mkdir(os.path.join(outdir, 'files'))

    for topic in tqdm.tqdm(topics, ncols=120, unit='topics', desc='Request data for topics', leave=False):
        get(BASE_URL, token, outdir, path=topic, limit=250)

def main():
    cli()
