from dataclasses import dataclass, field
from typing import Iterable

from aws_cdk.aws_lambda import Function
from aws_cdk.aws_s3 import Bucket, NotificationKeyFilter, EventType
from aws_cdk.aws_s3_notifications import LambdaDestination


@dataclass(frozen=True)
class BucketEvent:
    """
    S3 bucket events.

    Properties
    ==========

    ``event_type``
        S3 notification event type.
    ``key_filters``
        Key filters that are applied to the target bucket.
        For example, setting key filter suffix, specifies on which files changes, based on
        file type, should endpoint be updated. This is useful if updates are required only
        for SageMaker model objects, i.e.: "model.tar.gz".
    """

    event_type: EventType
    key_filters:  Iterable[NotificationKeyFilter] = field(default_factory=list)

    def bind(self, bucket: Bucket, handler: Function) -> None:
        return bucket.add_event_notification(self.event_type, LambdaDestination(handler), *self.key_filters)
