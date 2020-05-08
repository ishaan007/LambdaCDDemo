import json
import boto3
from elasticsearch import Elasticsearch
import certifi

# TODO: update
host = 'https://vpc-photos-cd-v3m6vhbcqpleevatzh2smo4wlm.us-east-1.es.amazonaws.com'  # the Amazon ES domain, including https://
index = 'photos-cd'

def disambiguate_query(query, userId):
    # return object is dict with slotvalues
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName='search_photos_bot',
        botAlias='search_photos_bot',
        userId=userId,
        inputText=query
    )
    print(response)
    slots = response['slots']
    res = []
    if slots['key_a'] is not None:
        key_a = slots['key_a']
        if key_a[-1] == 's':
            key_a = key_a[:-1]
        res.append(key_a)
    if slots['key_b'] is not None:
        key_b = slots['key_b']
        if key_b[-1] == 's':
            key_b = key_b[:-1]
        res.append(key_b)

    print(res)
    return res


def search_index(keywords):
    # Use elasticsearch library
    # es_host = es_domain_endpoint('photos-test')

    es = Elasticsearch([host],
                       ##[{'host': es_host, 'port': 443}  ], #
                       use_ssl=True,
                       ca_certs=certifi.where()
                       )

    # each entry in results should be of the form {url: string, labels: array (of strings)}
    if len(keywords) == 1:
        query = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "term": {"labels": keywords[0]}
                    }
                }
            }
        }
    elif len(keywords) == 2:
        query = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "term": {"labels": keywords[0]},
                        "term": {"labels": keywords[1]}
                    }
                }
            }
        }

    es_res = es.search(index=index, body=query)
    res = []
    for hit in es_res['hits']['hits']:
        obj = hit['_source']
        res.append({'url': ('https://' + obj['bucket'] + '.s3.amazonaws.com/' + obj['objectKey']), 'labels': obj['labels']})

    print(res)
    return res


def lambda_handler(event, context):
    # TODO implement
    print(event)
    query = event['query']
    userId = "dummy"  # does not matter since lex does not need to  keep state

    # 1) Pass query to Lex to get keywords
    keywords = disambiguate_query(query, userId)

    if not keywords:
        return {
            'statusCode': 200,
            'results': []
        }

    # 2) search elasticsearch for photos on the keywords
    results = search_index(keywords)

    return {
        'statusCode': 200,
        'results': results
    }
