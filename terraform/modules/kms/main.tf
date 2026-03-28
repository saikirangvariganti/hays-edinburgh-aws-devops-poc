variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "deletion_window_in_days" {
  description = "Key deletion window in days"
  type        = number
  default     = 30
}

resource "aws_kms_key" "eks" {
  description             = "CMK for EKS cluster secrets encryption"
  deletion_window_in_days = var.deletion_window_in_days
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow EKS to use the key"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "hays-eks-cmk-${var.environment}"
    Environment = var.environment
    Purpose     = "EKS secrets encryption"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "eks" {
  name          = "alias/hays-eks-${var.environment}"
  target_key_id = aws_kms_key.eks.key_id
}

resource "aws_kms_key" "rds" {
  description             = "CMK for RDS database encryption"
  deletion_window_in_days = var.deletion_window_in_days
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow RDS to use the key"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey",
          "kms:CreateGrant"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "hays-rds-cmk-${var.environment}"
    Environment = var.environment
    Purpose     = "RDS storage encryption"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/hays-rds-${var.environment}"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_kms_key" "s3" {
  description             = "CMK for S3 bucket encryption"
  deletion_window_in_days = var.deletion_window_in_days
  enable_key_rotation     = true

  tags = {
    Name        = "hays-s3-cmk-${var.environment}"
    Environment = var.environment
    Purpose     = "S3 bucket encryption"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/hays-s3-${var.environment}"
  target_key_id = aws_kms_key.s3.key_id
}

output "eks_kms_key_arn" {
  value = aws_kms_key.eks.arn
}

output "rds_kms_key_arn" {
  value = aws_kms_key.rds.arn
}

output "s3_kms_key_arn" {
  value = aws_kms_key.s3.arn
}

output "eks_kms_key_id" {
  value = aws_kms_key.eks.key_id
}
