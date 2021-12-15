import os

from b_aws_cdk_parallel.deployment_executor import DeploymentExecutor
from b_aws_cdk_parallel.deployment_type import DeploymentType
from b_aws_testing_framework.tools.cdk_testing.cdk_tool_config import CdkToolConfig

from .manager import MANAGER

DO_NOT_CREATE_INFRASTRUCTURE = int(os.environ.get('DO_NOT_CREATE_INFRASTRUCTURE', 0))


def inf_create():
    if DO_NOT_CREATE_INFRASTRUCTURE == 1:
        return

    def wrapper(cdk_config: CdkToolConfig):
        DeploymentExecutor(
            type=DeploymentType.DEPLOY,
            path=cdk_config.cdk_app_path,
            env=cdk_config.deployment_process_environment
        ).run()

    MANAGER.prepare_infrastructure(wrapper)


if __name__ == '__main__':
    inf_create()
