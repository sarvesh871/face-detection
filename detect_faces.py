import boto3
import json
import os
from pathlib import Path
import subprocess

bucket = os.environ["S3_BUCKET"]
region = os.environ["AWS_REGION"]

# Find image changed in the latest commit
result = subprocess.run(
    ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
    capture_output=True,
    text=True,
    check=True
)

changed_files = result.stdout.strip().splitlines()

image_path = None

for file in changed_files:
    if file.startswith("images/") and file.lower().endswith((".jpg", ".jpeg")):
        image_path = file
        break

if image_path is None:
    raise FileNotFoundError("No JPEG image found in the latest commit.")

image_name = Path(image_path).name

print(f"Processing image: {image_name}")

# ----------------------------
# Upload to S3
# ----------------------------
s3 = boto3.client("s3", region_name=region)

s3.upload_file(image_path, bucket, image_name)

print("Image uploaded successfully.")

# ----------------------------
# Detect Faces
# ----------------------------
rekognition = boto3.client("rekognition", region_name=region)

response = rekognition.detect_faces(
    Image={
        "S3Object": {
            "Bucket": bucket,
            "Name": image_name
        }
    },
    Attributes=["DEFAULT"]
)

faces = response["FaceDetails"]

print(f"Number of faces: {len(faces)}")

result = {
    "Image": image_name,
    "NumberOfFaces": len(faces),
    "Faces": []
}

for i, face in enumerate(faces, start=1):
    confidence = round(face["Confidence"], 2)

    print(f"Face {i} Confidence: {confidence}%")

    result["Faces"].append({
        "FaceNumber": i,
        "Confidence": confidence
    })

# ----------------------------
# Save JSON
# ----------------------------
with open("result.json", "w") as f:
    json.dump(result, f, indent=4)

print("result.json written successfully.")
