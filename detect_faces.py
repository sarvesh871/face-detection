import boto3
import json
import os
from pathlib import Path

bucket = os.environ["S3_BUCKET"]
region = os.environ["AWS_REGION"]

# ----------------------------
# Find the image that triggered this workflow
# ----------------------------
event_path = os.environ["GITHUB_EVENT_PATH"]

with open(event_path, "r") as f:
    event = json.load(f)

image_path = None

for commit in event.get("commits", []):
    for file in commit.get("added", []) + commit.get("modified", []):
        if file.startswith("images/") and (
            file.lower().endswith(".jpg")
            or file.lower().endswith(".jpeg")
        ):
            image_path = file

if image_path is None:
    raise FileNotFoundError("No image found in this commit.")

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
