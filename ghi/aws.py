import boto3
import json
import logging
import os
awslambda = boto3.client('lambda')


def InvokeSelf(event):

    functionName = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    event["headers"]["X-Ghi-Invoked"] = "true"

    logging.info("Received initial invocation. Invoking self a second time.")

    invoke = awslambda.invoke(
        FunctionName=functionName,
        InvocationType='Event',
        LogType='None',
        Payload=json.dumps(event)
    )
    if str(invoke['StatusCode'])[0] == '2':
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "message": "Request received."
            })
        }
    else:
        logging.error(invoke)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": "There was a problem processing request." 
            })
        }
