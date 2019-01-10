# Description
Repo contains simple setup to start DynamoDB locally in docker container and script to dump tables from AWS DynamoDB to local DynamoDB.  

# Dependencies
1. docker
2. python
3. docker-compose
4. aws-cli


# Usage
## Local usage of DynamoDB in Python
```python
import boto3                                                                                                    

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8001')                                     

list(dynamodb.tables.all())                                                                                     
```

## Dump tables from AWS DynamoDB to local DynamoDB
```
$ ./dump_dynamodb_tables.py --help
usage: dump_dynamodb_tables.py [-h] [--endpoint-url ENDPOINT_URL] table_regex

Dump table from AWS DynamoDB into local DynamoDB

positional arguments:
  table_regex

optional arguments:
  -h, --help            show this help message and exit
  --endpoint-url ENDPOINT_URL

```

**Example:**
1. run DynamoDB container
```
docker-compose up
```
2. run script to dump tables and wait until complete
```
$ ./dump_dynamodb_tables.py dev.*
```
