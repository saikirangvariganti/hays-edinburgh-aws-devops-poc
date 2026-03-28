#!/usr/bin/env bash
# KMS Customer Master Key (CMK) Setup Script
# Hays Edinburgh AWS DevOps POC
# Creates and configures KMS CMKs for EKS, RDS, and S3 encryption

set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-eu-west-2}"
ENVIRONMENT="${ENVIRONMENT:-production}"
ACCOUNT_ID=""
REPORT_FILE="kms_setup_report_$(date +%Y%m%d_%H%M%S).json"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

get_account_id() {
    ACCOUNT_ID=$(aws sts get-caller-identity \
        --query Account \
        --output text \
        --region "$REGION" 2>/dev/null)
    log "AWS Account ID: $ACCOUNT_ID"
    log "Region: $REGION"
    log "Environment: $ENVIRONMENT"
}

create_kms_key() {
    local purpose="$1"
    local alias="$2"
    local description="$3"

    log "Creating KMS CMK for $purpose..."

    # Build key policy
    local key_policy
    key_policy=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::${ACCOUNT_ID}:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow CloudWatch to use the key",
      "Effect": "Allow",
      "Principal": {
        "Service": "logs.${REGION}.amazonaws.com"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
EOF
)

    local key_id
    key_id=$(aws kms create-key \
        --description "$description" \
        --key-usage ENCRYPT_DECRYPT \
        --origin AWS_KMS \
        --policy "$key_policy" \
        --tags "TagKey=Environment,TagValue=${ENVIRONMENT}" "TagKey=Purpose,TagValue=${purpose}" "TagKey=ManagedBy,TagValue=terraform" \
        --region "$REGION" \
        --query 'KeyMetadata.KeyId' \
        --output text)

    log "Created KMS key: $key_id"

    # Enable key rotation
    aws kms enable-key-rotation \
        --key-id "$key_id" \
        --region "$REGION"
    log "Enabled annual key rotation for: $key_id"

    # Create alias
    local full_alias="alias/${alias}-${ENVIRONMENT}"
    if aws kms describe-key --key-id "$full_alias" --region "$REGION" 2>/dev/null; then
        log "Alias $full_alias already exists, updating..."
        aws kms update-alias \
            --alias-name "$full_alias" \
            --target-key-id "$key_id" \
            --region "$REGION"
    else
        aws kms create-alias \
            --alias-name "$full_alias" \
            --target-key-id "$key_id" \
            --region "$REGION"
    fi
    log "Created alias: $full_alias -> $key_id"

    echo "$key_id"
}

verify_key_rotation() {
    local key_id="$1"

    local rotation_status
    rotation_status=$(aws kms get-key-rotation-status \
        --key-id "$key_id" \
        --region "$REGION" \
        --query 'KeyRotationEnabled' \
        --output text)

    if [[ "$rotation_status" == "True" ]]; then
        log "PASS: Key rotation enabled for $key_id"
        return 0
    else
        log "FAIL: Key rotation NOT enabled for $key_id"
        return 1
    fi
}

list_existing_keys() {
    log "Listing existing CMKs in $REGION..."

    aws kms list-keys \
        --region "$REGION" \
        --query 'Keys[*].KeyId' \
        --output table 2>/dev/null || log "No existing keys or insufficient permissions"
}

generate_report() {
    local eks_key="$1"
    local rds_key="$2"
    local s3_key="$3"

    cat > "$REPORT_FILE" <<EOF
{
  "report_type": "KMS CMK Setup",
  "account_id": "${ACCOUNT_ID}",
  "region": "${REGION}",
  "environment": "${ENVIRONMENT}",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "keys_created": {
    "eks_secrets": {
      "key_id": "${eks_key}",
      "alias": "alias/hays-eks-${ENVIRONMENT}",
      "purpose": "EKS Kubernetes secrets encryption",
      "rotation_enabled": true
    },
    "rds_storage": {
      "key_id": "${rds_key}",
      "alias": "alias/hays-rds-${ENVIRONMENT}",
      "purpose": "RDS database storage encryption",
      "rotation_enabled": true
    },
    "s3_buckets": {
      "key_id": "${s3_key}",
      "alias": "alias/hays-s3-${ENVIRONMENT}",
      "purpose": "S3 bucket encryption",
      "rotation_enabled": true
    }
  },
  "next_steps": [
    "Update terraform.tfvars with the key ARNs above",
    "Reference keys in EKS encryption_config",
    "Reference keys in RDS storage_encrypted configuration",
    "Reference keys in S3 server_side_encryption_configuration"
  ]
}
EOF

    log "Report saved to: $REPORT_FILE"
}

main() {
    log "=== KMS CMK Setup — Hays Edinburgh DevOps POC ==="

    get_account_id

    log "Listing existing keys..."
    list_existing_keys

    log ""
    log "Creating CMKs for environment: $ENVIRONMENT"

    local eks_key
    eks_key=$(create_kms_key \
        "eks-secrets" \
        "hays-eks" \
        "CMK for EKS cluster secrets encryption - Hays DevOps POC")

    local rds_key
    rds_key=$(create_kms_key \
        "rds-storage" \
        "hays-rds" \
        "CMK for RDS database storage encryption - Hays DevOps POC")

    local s3_key
    s3_key=$(create_kms_key \
        "s3-encryption" \
        "hays-s3" \
        "CMK for S3 bucket server-side encryption - Hays DevOps POC")

    log ""
    log "Verifying key rotation settings..."
    verify_key_rotation "$eks_key"
    verify_key_rotation "$rds_key"
    verify_key_rotation "$s3_key"

    generate_report "$eks_key" "$rds_key" "$s3_key"

    log ""
    log "=== KMS Setup Complete ==="
    log "EKS Key:  $eks_key"
    log "RDS Key:  $rds_key"
    log "S3  Key:  $s3_key"
    log ""
    log "Add these to your terraform.tfvars:"
    log "  eks_kms_key_arn = \"arn:aws:kms:${REGION}:${ACCOUNT_ID}:key/${eks_key}\""
    log "  rds_kms_key_arn = \"arn:aws:kms:${REGION}:${ACCOUNT_ID}:key/${rds_key}\""
    log "  s3_kms_key_arn  = \"arn:aws:kms:${REGION}:${ACCOUNT_ID}:key/${s3_key}\""
}

main "$@"
