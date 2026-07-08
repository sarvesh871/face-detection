import boto3
import json
import os

bucket = os.environ["S3_BUCKET"]
region = os.environ["AWS_REGION"]

image_path = "images/employee.jpg"
image_name = os.path.basename(image_path)

# Upload to S3
s3 = boto3.client(
    "s3",
    region_name=region
)

s3.upload_file(image_path, bucket, image_name)

print("Image uploaded to S3")

# Rekognition
rekognition = boto3.client(
    "rekognition",
    region_name=region
)

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

print("Number of faces:", len(faces))

results = {
    "NumberOfFaces": len(faces),
    "Faces": []
}

for i, face in enumerate(faces, start=1):
    confidence = face["Confidence"]

    print(f"Face {i} Confidence: {confidence:.2f}%")

    results["Faces"].append({
        "Face": i,
        "Confidence": confidence
    })

with open("result.json", "w") as f:
    json.dump(results, f, indent=4)

print("result.json created")
