import os

from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyDocument, PolicyStatement, Effect
from aws_cdk.aws_s3 import Bucket, NotificationKeyFilter, EventType
from aws_cdk.aws_sagemaker import CfnEndpointConfigProps, CfnModelProps, CfnEndpointProps, CfnModel, CfnEndpointConfig
from aws_cdk.core import Construct, RemovalPolicy
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack
from b_cfn_s3_large_deployment.deployment_props import DeploymentProps
from b_cfn_s3_large_deployment.deployment_source import AssetDeploymentSource
from b_cfn_s3_large_deployment.resource import S3LargeDeploymentResource

from b_cfn_sagemaker_endpoint import SagemakerEndpoint, ModelProps, BucketEvent
from b_cfn_sagemaker_endpoint_tests.integration.utils.model_assets_utils import create_asset_options


class Infrastructure(TestingStack):
    TEST_SAGEMAKER_ENDPOINT_NAME_KEY = 'TestSagemakerEndpointKey'
    TEST_MODELS_BUCKET_NAME = 'TestModelsBucketName'

    def __init__(self, scope: Construct):
        super().__init__(scope=scope)

        test_bucket = Bucket(
            scope=self,
            id=f'{self.global_prefix()}BSagemakerModelsBucket',
            bucket_name=f'{self.global_prefix()}-b-sagemaker-models'.lower(),
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Upload two dummy SageMaker models to the test bucket, to be used
        # as a cache of objects for further interactions via boto3's S3 API.
        models_deployment = S3LargeDeploymentResource(
            scope=self,
            name=f'{self.global_prefix()}BModelsDeployment',
            sources=[
                AssetDeploymentSource(
                    path=os.path.join(os.path.dirname(__file__), 'data/models/v1'),
                    options=create_asset_options(model_name='v1')
                ),
                AssetDeploymentSource(
                    path=os.path.join(os.path.dirname(__file__), 'data/models/v2'),
                    options=create_asset_options(model_name='v2')
                )
            ],
            destination_bucket=test_bucket,
            props=DeploymentProps(
                destination_key_prefix='models/',
                retain_on_delete=False
            )
        )
        # Upload one of the two dummy SageMaker models to the test bucket, to be used
        # as the initial endpoint model.
        active_model_deployment = S3LargeDeploymentResource(
            scope=self,
            name=f'{self.global_prefix()}BActiveModelDeployment',
            sources=[
                AssetDeploymentSource(
                    path=os.path.join(os.path.dirname(__file__), 'data/models/v1'),
                    options=create_asset_options(model_name='v1')
                )
            ],
            destination_bucket=test_bucket,
            props=DeploymentProps(
                destination_key_prefix='active_model/',
                retain_on_delete=False
            )
        )
        active_model_deployment.node.add_dependency(models_deployment)

        test_role = Role(
            scope=self,
            id=f'{self.global_prefix()}BSagemakerTestRole',
            assumed_by=ServicePrincipal('sagemaker.amazonaws.com'),
            inline_policies={
                'SagemakerInferenceModelExecutionPolicy': PolicyDocument(
                    statements=[
                        PolicyStatement(
                            actions=[
                                'cloudwatch:PutMetricData',
                                'ecr:GetAuthorizationToken',
                                'ecr:BatchCheckLayerAvailability',
                                'ecr:GetDownloadUrlForLayer',
                                'ecr:BatchGetImage',
                                'logs:CreateLogStream',
                                'logs:PutLogEvents',
                                'logs:CreateLogGroup',
                                'logs:DescribeLogStreams',
                            ],
                            effect=Effect.ALLOW,
                            resources=['*']
                        ),
                        PolicyStatement(
                            actions=[
                                's3:PutObject',
                                's3:ListBucket',
                                's3:GetObject',
                                's3:DeleteObject',
                            ],
                            effect=Effect.ALLOW,
                            resources=[
                                test_bucket.bucket_arn,
                                test_bucket.arn_for_objects('active_model/*')
                            ]
                        )
                    ]
                )
            }
        )

        # Configure SageMaker test dummy model.
        dummy_model_data_s3_url = f's3://{test_bucket.bucket_name}/active_model/model.tar.gz'
        dummy_model_props = ModelProps(CfnModelProps(
            execution_role_arn=test_role.role_arn,
            model_name=f'{self.global_prefix()}-b-sagemaker-endpoint-test-dummy'.lower(),
            primary_container=CfnModel.ContainerDefinitionProperty(
                environment={
                    'SAGEMAKER_CONTAINER_LOG_LEVEL': 20,
                    'SAGEMAKER_PROGRAM': 'inference_code.py',
                    'SAGEMAKER_REGION': self.region,
                    'SAGEMAKER_SUBMIT_DIRECTORY': dummy_model_data_s3_url
                },
                image='763104351884.dkr.ecr.eu-central-1.amazonaws.com/huggingface-pytorch-inference:1.7.1-transformers4.6.1-cpu-py36-ubuntu18.04',
                mode='SingleModel',
                model_data_url=dummy_model_data_s3_url
            )
        ))

        # Setup SageMaker test endpoint configuration.
        dummy_endpoint_config_props = CfnEndpointConfigProps(
            production_variants=[
                CfnEndpointConfig.ProductionVariantProperty(
                    initial_instance_count=1,
                    initial_variant_weight=1.0,
                    instance_type='ml.t2.medium',
                    model_name=dummy_model_props.model_name,
                    variant_name='AllTraffic',
                )
            ],
            endpoint_config_name=f'{self.global_prefix()}-b-sagemaker-endpoint-test'.lower(),
        )

        # Configure & deploy SageMaker test endpoint.
        endpoint = SagemakerEndpoint(
            scope=self,
            id=f'{self.global_prefix()}BSagemakerEndpoint',
            endpoint_props=CfnEndpointProps(
                endpoint_config_name=dummy_endpoint_config_props.endpoint_config_name,
                endpoint_name=f'{self.global_prefix()}-b-sagemaker-endpoint-test'.lower(),
                retain_all_variant_properties=False
            ),
            endpoint_config_props=dummy_endpoint_config_props,
            models_props=[
                dummy_model_props
            ],
            models_bucket=test_bucket,
            bucket_events=[
                BucketEvent(EventType.OBJECT_CREATED, [
                    NotificationKeyFilter(prefix='active_model/', suffix='.tar.gz')
                ])
            ]
        )
        endpoint.node.add_dependency(active_model_deployment)

        self.add_output(self.TEST_SAGEMAKER_ENDPOINT_NAME_KEY, endpoint.endpoint_name)
        self.add_output(self.TEST_MODELS_BUCKET_NAME, test_bucket.bucket_name)
