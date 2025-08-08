import boto3
import csv
import io
from django.conf import settings
import os

def fetch_patient_data_from_s3():
    bucket_name = "access-bucket-sneha-project"
    key = "patients.csv"

    s3 = boto3.client("s3", region_name="us-east-1")
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    content = obj["Body"].read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))
    return list(reader)