import os
import boto3

def upload_static():
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        region_name="auto",
    )
    bucket = "charity-connect"
    static_dir = os.path.abspath("static")
    print(f"Uploading from {static_dir} to MinIO bucket '{bucket}'...")

    for root, _, files in os.walk(static_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, os.path.dirname(static_dir)).replace("\\", "/")
            key = rel_path
            content_type = "image/jpeg" if file.endswith((".jpeg", ".jpg")) else "image/png"
            with open(file_path, "rb") as f:
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=f.read(),
                    ContentType=content_type,
                )
            print(f"Uploaded {key}")

if __name__ == "__main__":
    upload_static()
