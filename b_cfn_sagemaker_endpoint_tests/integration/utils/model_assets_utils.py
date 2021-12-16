from typing import List

from aws_cdk.aws_s3_assets import AssetOptions
from aws_cdk.core import AssetHashType, BundlingOptions, DockerImage


def create_asset_options(model_name: str) -> AssetOptions:
    """
    Create asset options that are configured to bundle model files
    as "/asset-output/``model_name``/model.tar.gz".

    :param model_name: Model directory name.

    :return: Bundled asset options.
    """

    return AssetOptions(
        asset_hash_type=AssetHashType.OUTPUT,
        bundling=BundlingOptions(
            image=DockerImage.from_registry('ubuntu:20.04'),
            command=['bash', '-c', ' && '.join(__make_build_command(model_name))]
        )
    )


def __make_build_command(model_name: str) -> List[str]:
    return [
        # Copy.
        'mkdir -p /tmp/asset-output',
        'ls -R /tmp',
        'cp -R /tmp/asset-output/. /asset-output/.',
        'cp -R /asset-input/. /asset-output/.',

        # Cleanup.
        'find /asset-output/ -type f -name "*.py[co]" -delete',
        'find /asset-output/ -type d -name "__pycache__" -exec rm -rf {} +',
        'find /asset-output/ -type d -name "*.dist-info" -exec rm -rf {} +',
        'find /asset-output/ -type d -name "*.egg-info" -exec rm -rf {} +',
        'rm -f /asset-output/__init__.py',

        # Archive and compress model files.
        'prev_workdir="$(pwd)"',
        'cd /asset-output',
        'tar -czf model.tar.gz *',
        'cd $prev_workdir',

        # Remove leftover uncompressed files.
        'find /asset-output/* -not -name "model.tar.gz" -type f -or -type d -exec rm -rf {} +',

        f'mkdir /asset-output/{model_name}',
        f'mv  /asset-output/model.tar.gz /asset-output/{model_name}/',

        # Validation.
        'ls -Rla /asset-output',
        'find /asset-output/ -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum'
    ]
