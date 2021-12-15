import os

from b_aws_testing_framework.credentials import Credentials
from b_aws_testing_framework.tools.cdk_testing.cdk_tool_config import CdkToolConfig
from b_aws_testing_framework.tools.cdk_testing.testing_manager import TestingManager

GLOBAL_PREFIX = os.environ.get('GLOBAL_PREFIX')
CDK_PATH = f'{os.path.dirname(os.path.abspath(__file__))}'
MANAGER = TestingManager(Credentials(), CdkToolConfig(CDK_PATH, destroy_before_preparing=True))

if GLOBAL_PREFIX:
    MANAGER.set_global_prefix(f'B{GLOBAL_PREFIX[:10]}')
