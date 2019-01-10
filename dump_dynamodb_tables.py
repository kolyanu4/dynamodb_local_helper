#!/usr/bin/env python
"""
Takes all tables that fulfill the regexp and create them in local DynamoDB
"""
import argparse
import logging
import re
import sys

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(fmt)

logger.addHandler(handler)
logger.propagate = False


def dump_tables(aws_dynamodb, localhost_dynamodb, tables_to_dump):
    for table_name in tables_to_dump:
        logger.debug('Processing table %s', table_name)
        try:
            described_table = aws_dynamodb.meta.client.describe_table(TableName=table_name)['Table']
        except aws_dynamodb.ResourceNotFoundException:
            logger.error('Database with name "%s" was not found. Probably it was deleted', table_name)
            continue

        localhost_table = localhost_dynamodb.create_table(
            TableName=table_name,
            KeySchema=described_table['KeySchema'],
            AttributeDefinitions=described_table['AttributeDefinitions'],
            ProvisionedThroughput={
                'ReadCapacityUnits': 100,
                'WriteCapacityUnits': 100,
            }
        )

        for item in aws_dynamodb.Table(table_name).scan()['Items']:
            with localhost_table.batch_writer() as batch:
                batch.put_item(Item=item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump table from AWS DynamoDB into local DynamoDB')
    parser.add_argument('table_regex', type=str)
    parser.add_argument('--endpoint-url', type=str, default='http://localhost:8001')
    options = parser.parse_args()

    try:
        compiled_regex = re.compile(options.table_regex)
        logger.info('Going to dump all tables that satisfy the regex "%s"', options.table_regex)
    except re.error:
        logger.exception('Not valid python regex')
        sys.exit(-1)

    aws_dynamodb = boto3.resource('dynamodb')
    localhost_dynamodb = boto3.resource('dynamodb', endpoint_url=options.endpoint_url)

    tables_to_dump = [table.name for table in aws_dynamodb.tables.all() if compiled_regex.match(table.name)]
    logger.debug('Found %s tables to dump', len(tables_to_dump))

    dump_tables(aws_dynamodb, localhost_dynamodb, tables_to_dump)
    logger.info('Finished')
