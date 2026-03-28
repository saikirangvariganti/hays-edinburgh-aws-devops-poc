terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket         = "hays-terraform-state"
    key            = "devops/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
    dynamodb_table = "hays-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "hays-devops-poc"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

module "kms" {
  source      = "./modules/kms"
  environment = var.environment
  account_id  = var.account_id
}

module "vpc" {
  source      = "./modules/vpc"
  environment = var.environment
}

module "iam" {
  source      = "./modules/iam"
  environment = var.environment
  cluster_name = "hays-devops-eks"
}

module "eks" {
  source             = "./modules/eks"
  cluster_name       = "hays-devops-eks"
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  cluster_role_arn   = module.iam.eks_cluster_role_arn
  node_role_arn      = module.iam.eks_node_role_arn
  kms_key_arn        = module.kms.eks_kms_key_arn
}

module "rds" {
  source       = "./modules/rds"
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
  kms_key_arn  = module.kms.rds_kms_key_arn
  db_password  = var.db_password
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

module "s3_artifacts" {
  source      = "./modules/s3"
  bucket_name = "hays-devops-artifacts-${var.environment}"
  environment = var.environment
  kms_key_arn = module.kms.s3_kms_key_arn
}

module "s3_backups" {
  source      = "./modules/s3"
  bucket_name = "hays-devops-backups-${var.environment}"
  environment = var.environment
  kms_key_arn = module.kms.s3_kms_key_arn
}
