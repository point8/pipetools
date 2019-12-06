# 🛴 Command line tools for Pipedrive CRM

## Command-line Interface

```
$ pipetools --help
Usage: pipetools [OPTIONS] COMMAND [ARGS]...

  Command line tools for Pipedrive CRM

Options:
  --help  Show this message and exit.

Commands:
  backup  Run Pipedrive CRM data backup
  deal    Fetch deal as JSON with DEALID (e.g. 42)
```

### Fetch backup data from Pipedrive instance

```
$ pipetools backup --help
Usage: pipetools backup [OPTIONS] [OUTDIR]

  Run Pipedrive CRM data backup

Options:
  --token TEXT                    Pipedrive CRM API token
  --topic [users|deals|persons|organizations|pipelines|stages|files|activities]
                                  Select topic
  --stdout                        Output to stdout instead of file
  --help                          Show this message and exit.
```

### Fetch single deal from Pipedrive instance

```
$ pipetools backup --help
Usage: pipetools deal [OPTIONS] DEALID

  Fetch deal as JSON with DEALID (e.g. 42)

Options:
  --outdir TEXT  Set directory to save JSON file
  --token TEXT   Pipedrive CRE API token
  --stdout       Output to stdout instead of file
  --help         Show this message and exit.
```

#### Example

```
pipetools backup --token=123456790
pipetools deal 315 --token 1234567890
```
