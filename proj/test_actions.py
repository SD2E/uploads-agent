import json
from .celery import app
from .tasks import process_fsevent_wkflw

EVENT = '{"EventName":"s3:ObjectCreated:Put","Key":"uploads/tacc/202001/M87.jpg","Records":[{"eventVersion":"2.0","eventSource":"minio:s3","awsRegion":"us-east-1","eventTime":"2019-11-22T00:56:36Z","eventName":"s3:ObjectCreated:Put","userIdentity":{"principalId":"DUKHBJTT0KREC5A9FI4U"},"requestParameters":{"accessKey":"DUKHBJTT0KREC5A9FI4U","region":"us-east-1","sourceIPAddress":"72.182.34.155"},"responseElements":{"x-amz-request-id":"15D95615C4D99F3A","x-minio-deployment-id":"a2b41da7-a0f6-43e7-8fab-190d42366269","x-minio-origin-endpoint":"http://129.114.52.102:9001"},"s3":{"s3SchemaVersion":"1.0","configurationId":"Config","bucket":{"name":"uploads","ownerIdentity":{"principalId":"DUKHBJTT0KREC5A9FI4U"},"arn":"arn:aws:s3:::uploads"},"object":{"key":"tacc%2F202001%2FM87.jpg","size":308101,"eTag":"4cec3cd3d449f6aa417b7e785043fd25","contentType":"image/jpeg","userMetadata":{"content-type":"image/jpeg"},"versionId":"1","sequencer":"15D95615C5ED9B4D"}},"source":{"host":"","port":"","userAgent":"Cyberduck/7.1.2.31675 (Mac OS X/10.14.6) (x86_64)"}}]}'


__all__ = ['test_event']


@app.task
def test_event():
    event = json.loads(EVENT)
    process_fsevent_wkflw.delay(event)
