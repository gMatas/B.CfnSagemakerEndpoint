# B.CfnSagemakerEndpoint

**b-cfn-sagemaker-endpoint** - AWS CloudFormation resource that handles the deployment and update of 
SageMaker models endpoint.

### Description

This resource handles the deployment and update of SageMaker models endpoint. It is designed to 
enable automatic update of SageMaker's models endpoint in the event of modifying the source model data. 
This is achieved by utilizing S3's' event notifications. On updating the target S3 bucket objects, 
an event is emitted that is handled by a lambda function which updates the deployed SageMaker endpoint.

Endpoint update is done via `boto3`'s function `update_endpoint()` that requires a new 
configuration to be provided. Instead of creating a new instance of it each time, two identical 
configurations (A & B) with different names are created only once, during the deployment. Each 
`update_endpoint()` call effectively swaps them together, allowing the endpoint to be refreshed with new 
up-to-date source model(-s) data.

### Remarks

[Biomapas](https://biomapas.com) aims to modernise life-science
industry by sharing its IT knowledge with other companies and
the community.

### Related technology

- Python >= 3.8
- Amazon Web Services (AWS)

### Assumptions

The project assumes that the person working with it have basic knowledge in python
programming.

### Useful sources

See code documentation for any additional sources and references.

### Install

Use the package manager pip to install this package. This project is not in the PyPi
repository yet. Install directly from source or PyPI.

```bash
pip install .
```

Or

```bash
pip install b-cfn-sagemaker-endpoint
```

### Usage & Examples

This resource handles ``aws-cdk.aws-sagemaker`` library's resources: ``CnfModel``, ``CnfEndpointConfig`` & 
``CnfEndpoint`` deployment. The user is tasked only to provide configurations for each of these items via their 
properties, i.e.: ``CnfModelProps`` -> ``CnfModel``, that on themselves do not create any resources.

To deploy a SageMaker model(-s) endpoint the following steps have to be taken:

1. Configure SageMaker model properties as a ``ModelProps`` class object:
    ```python
    example_model_props = ModelProps(
        props=CfnModelProps(...),
        custom_id=..., # (optional) If not provided, it is generated automatically.
    )
    ```
2. Setup SageMaker endpoint configuration properties as ``CfnEnpointConfigProps``:
    ```python
    example_endpoint_config_props = CfnEndpointConfigProps(...)
    ```
3. Configure SageMaker endpoint properties as ``CfnEnpointProps``:
    ```python
    example_endpoint_props = CfnEndpointProps(...)
    ```
4. Finally, setup ``B.CfnSagemakerEndpoint``'s ``SagemakerEndpoint`` resource using previously defined 
   properties:
    ```python
    SagemakerEndpoint(
        scope=...,
        id='your-scoped-cdk-resource-id',
        endpoint_props=example_endpoint_props,
        endpoint_config_props=example_endpoint_config_props,
        models_props=[
            example_model_props
        ],
        models_bucket=Bucket(...),
        # Optional. If no explicit bucket events are provided, `EventType.OBJECT_CREATED` 
        # events are emitted for all bucket objects.
        bucket_events=[
            BucketEvent(EventType.OBJECT_CREATED, [
                NotificationKeyFilter(...)
            ])
        ]
    )
    ```
    
Once, ``SagemakerEndpoint`` is deployed, any changes in the source models bucket specified by 
``bucket_events``, starts endpoint update/refresh. During this time, it's status becomes "Updating" 
& no further update calls are handled.

### Known limits

Changing settings of ``CfnModel`` or ``CfnEndpointConfig`` resources, does not update the ``CfnEndpoint`` 
resource itself. To achieve this functionality, likely, a low-level CustomResource implementation would be 
required.

### Testing

ToDo

### Contribution

Found a bug? Want to add or suggest a new feature? Contributions of any kind are gladly
welcome. Contact your direct supervisor, create a pull-request or an issue in Jira platform.
