from aws_cdk.core import App

from b_cfn_sagemaker_endpoint_tests.integration.infrastructure import Infrastructure

# Initiate CDK applications and synthesize it.
app = App()
Infrastructure(app)
app.synth()
