output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.rds_endpoint
}

output "artifacts_bucket" {
  description = "S3 artifacts bucket name"
  value       = module.s3_artifacts.bucket_name
}

output "cicd_role_arn" {
  description = "CI/CD IAM role ARN"
  value       = module.iam.cicd_role_arn
}

output "eks_kms_key_arn" {
  description = "KMS key ARN for EKS"
  value       = module.kms.eks_kms_key_arn
}
