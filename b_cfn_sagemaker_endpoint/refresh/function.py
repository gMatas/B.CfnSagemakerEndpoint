import os

from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_sagemaker import CfnEndpoint, CfnEndpointConfig
from aws_cdk.core import Construct, Stack, Duration


class RefreshFunction(Function):
    """
    Lambda function that handles update/refresh of SageMaker model(-s) endpoint.

    Endpoint update is initialized via ``boto3``'s function ``update_endpoint()`` that requires a new
    configuration to be provided. Instead of creating a new instance of it each time, two identical
    configurations (A & B) with different names are created only once. Each ``update_endpoint()`` call
    effectively swaps them together, allowing the endpoint to be refreshed with new up-to-date source model(-s)
    data.

    :param scope: Construct scope.
    :param id: Scoped id of the resource.
    :param endpoint: SageMaker endpoint resource.
    :param endpoint_config_a: SageMaker endpoint configuration A resource. See README.
    :param endpoint_config_b: SageMaker endpoint configuration B resource. See README.
    :param wait_time: Time to wait before endpoint is updated. It is useful to wait before
        handling s3 bucket events as there can be multiple other in-flight events coming.
    """

    from . import source
    SOURCE_PATH = os.path.dirname(source.__file__)

    def __init__(
            self,
            scope: Construct,
            id: str,
            endpoint: CfnEndpoint,
            endpoint_config_a: CfnEndpointConfig,
            endpoint_config_b: CfnEndpointConfig,
            wait_time: float
    ):
        current_stack = Stack.of(scope)
        region = current_stack.region
        account = current_stack.account
        endpoint_name = endpoint.attr_endpoint_name
        endpoint_config_a_name = endpoint_config_a.attr_endpoint_config_name
        endpoint_config_b_name = endpoint_config_b.attr_endpoint_config_name
        super().__init__(
            scope,
            id,
            code=Code.from_asset(self.SOURCE_PATH),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_8,
            environment={
                'WAIT_TIME': str(wait_time),
                'SAGEMAKER_ENDPOINT_NAME': endpoint.endpoint_name,
                'SAGEMAKER_ENDPOINT_CONFIG_A_NAME': endpoint_config_a_name,
                'SAGEMAKER_ENDPOINT_CONFIG_B_NAME': endpoint_config_b_name,
            },
            function_name=id,
            initial_policy=[
                PolicyStatement(
                    actions=[
                        'sagemaker:DescribeEndpoint',
                        'sagemaker:UpdateEndpoint',
                        'sagemaker:CreateEndpointConfig',
                        'sagemaker:DescribeEndpointConfig',
                        'sagemaker:DeleteEndpointConfig',
                    ],
                    effect=Effect.ALLOW,
                    resources=[
                        f'arn:aws:sagemaker:{region}:{account}:endpoint/{endpoint_name}',
                        f'arn:aws:sagemaker:{region}:{account}:endpoint-config/{endpoint_config_a_name}',
                        f'arn:aws:sagemaker:{region}:{account}:endpoint-config/{endpoint_config_b_name}',
                    ]
                )
            ],
            timeout=Duration.minutes(15),
            max_event_age=Duration.seconds(60),
            # This lambda function's concurrency must be limited to only single execution at a given
            # time. This is because it is called by multiple asynchronous S3 bucket events, that can
            # result in a race condition.
            reserved_concurrent_executions=1
        )
