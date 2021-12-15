import json
import os
import time
from typing import Any, Dict

import boto3


def handler(event: Dict[str, Any], context: Any) -> None:
    print(f'S3 event received: {json.dumps(event)}')

    wait_time = float(os.environ['WAIT_TIME'])
    endpoint_name = os.environ['SAGEMAKER_ENDPOINT_NAME']
    endpoint_config_a_name = os.environ['SAGEMAKER_ENDPOINT_CONFIG_A_NAME']
    endpoint_config_b_name = os.environ['SAGEMAKER_ENDPOINT_CONFIG_B_NAME']
    print(
        'Using the following environment variables: '
        f'{wait_time=} '
        f'{endpoint_name=} '
        f'{endpoint_config_a_name=} '
        f'{endpoint_config_b_name=} '
    )

    # Wait for any other bucket objects to be uploaded.
    # NOTE: Waiting here until all files are uploaded to s3 bucket is necessary before
    #   calling ``update_endpoint()`` function. Since multiple files will not be uploaded
    #   to the bucket at the same time. Therefore, premature ``update_endpoint`` call
    #   might fail to pull all the required files from s3.
    print('Waiting on standby...')
    time.sleep(wait_time)

    sagemaker_client = boto3.client('sagemaker')

    endpoint_description = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
    active_endpoint_config_name = endpoint_description['EndpointConfigName']
    print(f'Currently active endpoint configuration name: "{active_endpoint_config_name}"')
    # Handles A & B endpoint configurations names swapping. See ``RefreshFunction`` docs
    # or README for more information about it.
    new_endpoint_config_name = {
        endpoint_config_a_name: endpoint_config_b_name,
        endpoint_config_b_name: endpoint_config_a_name,
    }[active_endpoint_config_name]

    sagemaker_client.update_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=new_endpoint_config_name,
        RetainAllVariantProperties=False
    )
    print(f'Endpoint started being updated to a new endpoint configuration: "{new_endpoint_config_name}"')
