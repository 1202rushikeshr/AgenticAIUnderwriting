import boto3

textract = boto3.client("textract")

def extract_text_from_document(s3_bucket, s3_key):
    response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}}
    )

    lines = [
        block["Text"]
        for block in response["Blocks"]
        if block["BlockType"] == "LINE"
    ]
    return "\n".join(lines)
