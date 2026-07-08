import boto3
import json
import os
from pathlib import Path

bucket = os.environ["S3_BUCKET"]
region = os.environ["AWS_REGION"]

# ----------------------------
# Find the newest JPEG image
# ----------------------------
images_dir = Path("images")

image_files = list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.jpg"))

if not image_files:
    raise FileNotFoundError("No JPEG image found inside images folder.")

latest_image = max(image_files, key=lambda x: x.stat().st_mtime)

image_path = str(latest_image)
image_name = latest_image.name

print(f"Using image: {image_name}")

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
