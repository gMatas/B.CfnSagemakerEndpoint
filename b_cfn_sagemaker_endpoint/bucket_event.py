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
    """

    event_type: EventType
    key_filters:  Iterable[NotificationKeyFilter] = field(default_factory=list)

    def bind(self, bucket: Bucket, handler: Function) -> None:
        return bucket.add_event_notification(self.event_type, LambdaDestination(handler), *self.key_filters)
