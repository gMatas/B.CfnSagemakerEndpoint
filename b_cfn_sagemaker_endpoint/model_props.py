from dataclasses import dataclass

from aws_cdk.aws_sagemaker import CfnModelProps, CfnModel
from aws_cdk.core import Construct


@dataclass(frozen=True)
class ModelProps:
    """
    SageMaker model properties.

    More info at: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-model.html

    Properties
    ==========

    ``model_name``
        SageMaker inference model name.
    ``props``
        Properties for defining a ``AWS::SageMaker::Model``. ``CfnModelProps.model_name``
        property has no effect as ``ModelProps.model_name`` is used instead.
    ``custom_id``
        Optional. Custom CDK resource id. By default id is generated automatically.
    """

    model_name: str
    props: CfnModelProps
    custom_id: str = None

    def __post_init__(self):
        if self.props.model_name and self.model_name != self.props.model_name:
            raise ValueError(
                'Model name mismatch! Make sure that ``model_name`` '
                'matches ``CfnModelProps.model_name``.'
            )

    def __hash__(self):
        return hash(self.model_name)

    def bind(self, scope: Construct) -> CfnModel:
        return CfnModel(
            scope,
            self.custom_id or f'{self.model_name}-model',
            containers=self.props.containers,
            enable_network_isolation=self.props.enable_network_isolation,
            execution_role_arn=self.props.execution_role_arn,
            inference_execution_config=self.props.inference_execution_config,
            model_name=self.model_name,
            primary_container=self.props.primary_container,
            tags=self.props.tags,
            vpc_config=self.props.vpc_config,
        )
