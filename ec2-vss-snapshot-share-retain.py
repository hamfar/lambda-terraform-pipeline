####################################################################################
#   AWS Lambda function which shares all snapshots to  AWS account which has configured tags
#   and applies a configured retention policy to snapshots on Primary account 
#   environment variable "snapshot_tag_filter" needs to be set to exact filter requirements
#   e.g : {"Name": "tag:AppConsistent", "Values": ["True"]},{"Name": "tag:Name", "Values": ["ServerName"]}
#
####################################################################################
import json
import os
import boto3
import datetime

# The below code is used to handle timezones correctly
zero = datetime.timedelta(0)


class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return zero

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return zero

utc = UTC()

snapshot_retention_days = os.environ.get("snapshot_retention_days")
region = os.getenv("region")
share_account_id = os.getenv("share_account_id")
snapshot_tag_filter = eval(os.environ.get("snapshot_tag_filter"))

client = boto3.client("ec2",region)
resource = boto3.resource("ec2")

def lambda_handler(event, context):
    list_of_snapshots = []
    list_of_snapshots = client.describe_snapshots(
        Filters=snapshot_tag_filter
    )
    for snapshot in list_of_snapshots["Snapshots"]:
        snapshot_resource = resource.Snapshot(snapshot["SnapshotId"])
        snapshot_attribute = snapshot_resource.describe_attribute(Attribute="createVolumePermission")
        if snapshot_attribute["CreateVolumePermissions"] and snapshot_attribute["CreateVolumePermissions"][0]["UserId"] == share_account_id:
            print(f' Already shared with account { share_account_id } ')
            print(f' check { snapshot["SnapshotId"] } age ')
            snapshot_date = snapshot["StartTime"]
            now = datetime.datetime.now(utc)
            snapshot_age = now - snapshot_date
            if snapshot_age.days > int(snapshot_retention_days):
                print(f' {snapshot["SnapshotId"] } older than { snapshot_retention_days } days ')
                print(f' Deleting Snapshot { snapshot["SnapshotId"] } ')
                client.delete_snapshot(
                    SnapshotId=snapshot["SnapshotId"]
                    )
        else:
            print(f' Sharing with account { share_account_id } ')
            snapshot_resource.modify_attribute(
                Attribute="createVolumePermission",
                OperationType="add",
                UserIds=[share_account_id]
            )
