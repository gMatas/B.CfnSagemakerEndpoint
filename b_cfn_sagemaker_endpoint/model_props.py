from dataclasses import dataclass

from aws_cdk.aws_sagemaker import CfnModelProps, CfnModel
from aws_cdk.core import Construct


@dataclass
class ModelProps:
    """
    SageMaker model properties.

    More info at: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html

    Properties
    ==========

    ``props``
        Properties for defining a ``AWS::SageMaker::Model``.
    ``custom_id``
        Custom CDK resource id. By default id is generated automatically.
    """

    props: CfnModelProps
    custom_id: str = None

    @property
    def model_name(self) -> str:
        return self.props.model_name

    def bind(self, scope: Construct) -> CfnModel:
        return CfnModel(
            scope,
            self.custom_id or f'{self.props.model_name}-model',
            containers=self.props.containers,
            enable_network_isolation=self.props.enable_network_isolation,
            execution_role_arn=self.props.execution_role_arn,
            inference_execution_config=self.props.inference_execution_config,
            model_name=self.props.model_name,
            primary_container=self.props.primary_container,
            tags=self.props.tags,
            vpc_config=self.props.vpc_config,
        )
