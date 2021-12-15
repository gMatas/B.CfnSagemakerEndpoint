from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

with open('VERSION') as file:
    VERSION = file.read()
    VERSION = ''.join(VERSION.split())

setup(
    name='b-cfn-sagemaker-endpoint',
    version=VERSION,
    license='Apache License 2.0',
    packages=find_packages(exclude=[
        # Exclude virtual environment.
        'venv',
        # Exclude test source files.
        'b_cfn_sagemaker_endpoint_tests',
        'b_cfn_sagemaker_endpoint_tests.*',
    ]),
    description=(
        'AWS CloudFormation resource that handles the deployment and update of SageMaker models endpoint.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'aws-cdk.aws-iam>=1.90.0,<2.0.0',
        'aws-cdk.aws-lambda>=1.90.0,<2.0.0',
        'aws-cdk.aws-sagemaker>=1.90.0,<2.0.0',
        'aws-cdk.aws-ssm>=1.90.0,<2.0.0',
        'aws-cdk.aws-s3>=1.90.0,<2.0.0',
        'aws-cdk.aws-s3-assets>=1.90.0,<2.0.0',
        'aws-cdk.aws-s3-notifications>=1.90.0,<2.0.0',
        'aws-cdk.core>=1.90.0,<2.0.0',

        'b-aws-cdk-parallel>=2.2.0,<3.0.0',
        'b-aws-testing-framework>=0.6.0,<2.0.0',
        'b-cfn-s3-large-deployment>=1.1.2,<2.0.0',

        'boto3>=1.18.32<2.0.0',
        'urllib3>=1.26.6,<2.0.0',
    ],
    author='Matas Gumbinas',
    author_email='matas.gumbinas@biomapas.com',
    keywords='aws cdk sagemaker sagemaker-endpoint sagemaker-deployment python',
    url='https://github.com/Biomapas/B.CfnSagemakerEndpoint',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
