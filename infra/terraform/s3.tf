# Random ID para garantizar nombre único global en S3
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Bucket S3 Privado para Archivos Media
resource "aws_s3_bucket" "media" {
  bucket        = "${local.name_prefix}-media-${random_id.bucket_suffix.hex}"
  force_destroy = false

  tags = local.common_tags
}

# Bloquear TODO acceso público directo al Bucket
resource "aws_s3_bucket_public_access_block" "media_privacy" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cifrado por defecto SSE-S3
resource "aws_s3_bucket_server_side_encryption_configuration" "media_encryption" {
  bucket = aws_s3_bucket.media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Control de propiedad de objetos S3
resource "aws_s3_bucket_ownership_controls" "media_ownership" {
  bucket = aws_s3_bucket.media.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
