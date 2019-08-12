# Delete IAM User

## Usage

```bash
python iam_delete_user.py [--user-name]
```

## Logging

Logs with logging level `WARNING` are written to `logs.txt`.

## Help

```bash
python iam_delete_user.py --help
Usage: iam_delete_user.py [OPTIONS]

Options:
  --user-name TEXT  Name of the user.
  --dry-run         Echo AWS CLI commands without executing them.
  --help            Show this message and exit.
```
