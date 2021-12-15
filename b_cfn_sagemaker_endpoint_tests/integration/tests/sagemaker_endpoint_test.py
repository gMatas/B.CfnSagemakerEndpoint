import json

from b_aws_testing_framework.credentials import Credentials

from b_cfn_sagemaker_endpoint_tests.integration.infrastructure import Infrastructure


def test_INFRASTRUCTURE_sagemaker_endpoint_WITH_invocation_EXPECT_success_message():
    boto_session = Credentials().boto_session
    test_endpoint_name = Infrastructure.get_output(Infrastructure.TEST_SAGEMAKER_ENDPOINT_NAME_KEY)

    sagemaker_client = boto_session.client('sagemaker-runtime')
    response = sagemaker_client.invoke_endpoint(
        EndpointName=test_endpoint_name,
        Body='Nothing in particular.'
    )
    response_body = json.loads(response['Body'].read().decode())
    message = response_body['message']
    assert message == "Everything's Gucci! <3"
    print(message)
