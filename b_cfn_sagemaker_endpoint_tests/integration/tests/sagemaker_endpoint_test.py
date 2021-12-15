import json
import time
from typing import Any, Dict

from b_aws_testing_framework.credentials import Credentials

from b_cfn_sagemaker_endpoint_tests.integration.infrastructure import Infrastructure


def test_INFRASTRUCTURE_sagemaker_endpoint_update_WITH_invocations_EXPECT_updated_response():
    test_endpoint_name = Infrastructure.get_output(Infrastructure.TEST_SAGEMAKER_ENDPOINT_NAME_KEY)
    test_models_bucket_name = Infrastructure.get_output(Infrastructure.TEST_MODELS_BUCKET_NAME)

    boto_session = Credentials().boto_session

    def invoke_endpoint(body: str = None) -> Dict[str, Any]:
        sagemaker_runtime_client = boto_session.client('sagemaker-runtime')
        response = sagemaker_runtime_client.invoke_endpoint(
            EndpointName=test_endpoint_name,
            Body=body or 'Nothing in particular.'
        )
        return json.loads(response['Body'].read().decode())

    result = invoke_endpoint()
    message = result['message']
    assert message == "Everything's Gucci! <3", 'Failed to receive valid response.'

    # Resolve the next model the endpoint will be updated with.
    initial_model_name = result['model_name']
    model_names_swap_map = {
        'v1': 'v2',
        'v2': 'v1'
    }
    next_model_name = model_names_swap_map[initial_model_name]

    # Replace previous model files with the new.
    s3_resource = boto_session.resource('s3')
    models_bucket = s3_resource.Bucket(test_models_bucket_name)
    copy_source = {
        'Bucket': models_bucket.name,
        'Key': f'models/{next_model_name}/model.tar.gz'
    }
    models_bucket.copy(copy_source, 'active_model/model.tar.gz')
    time.sleep(10)

    # Wait for SageMaker endpoint to finish updating.
    print('Updating SageMaker endpoint. This might take a while - get some coffee...')
    sagemaker_client = boto_session.client('sagemaker')
    waiter = sagemaker_client.get_waiter('endpoint_in_service')
    waiter.wait(
        EndpointName=test_endpoint_name,
        WaiterConfig={
            'Delay': 30,
            'MaxAttempts': 120
        }
    )
    print('SageMaker endpoint updated!')

    result = invoke_endpoint()
    message = result['message']
    updated_model_name = result['model_name']
    assert message == "Everything's Gucci! <3", 'Failed to receive valid response.'

    assert updated_model_name != initial_model_name, 'Endpoint failed to be updated a new model.'
    assert updated_model_name == next_model_name, 'Endpoint updated with the wrong model.'

    print(message)
