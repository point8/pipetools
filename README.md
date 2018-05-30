# 🛴 Command line tools for Pipedrive CRM

## CLI

```
$ pipetools --help
Usage: pipetools [OPTIONS] COMMAND [ARGS]...

  Command line tools for Pipedrive CRM

Options:
  --help  Show this message and exit.

Commands:
  backup  Run Pipedrive CRM data backup
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

#### Example

```
pipetools backup --token=123456790
```
