# Terraform Module Builder - Implementation Guide & Code Recipes

## Remote State Configuration

```hcl
# backend.tf

terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "production/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# State locking table
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

## EKS Module Example

```hcl
# modules/eks/main.tf

resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  version  = var.cluster_version
  role_arn = aws_iam_role.cluster.arn

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = var.endpoint_private_access
    endpoint_public_access  = var.endpoint_public_access
    security_group_ids      = [aws_security_group.cluster.id]
  }

  encryption_config {
    provider {
      key_arn = var.kms_key_arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = var.enabled_log_types

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_iam_role_policy_attachment.vpc_resource_controller,
  ]

  tags = var.tags
}

resource "aws_eks_node_group" "main" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = each.key
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.subnet_ids

  instance_types = each.value.instance_types
  capacity_type  = each.value.capacity_type
  disk_size      = each.value.disk_size

  scaling_config {
    desired_size = each.value.desired_size
    max_size     = each.value.max_size
    min_size     = each.value.min_size
  }

  update_config {
    max_unavailable_percentage = 25
  }

  labels = each.value.labels

  dynamic "taint" {
    for_each = each.value.taints
    content {
      key    = taint.value.key
      value  = taint.value.value
      effect = taint.value.effect
    }
  }

  tags = merge(var.tags, each.value.tags)

  depends_on = [
    aws_iam_role_policy_attachment.node_policy,
    aws_iam_role_policy_attachment.cni_policy,
    aws_iam_role_policy_attachment.ecr_policy,
  ]

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# modules/eks/variables.tf

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "Map of node group configurations"
  type = map(object({
    instance_types = list(string)
    capacity_type  = string
    disk_size      = number
    desired_size   = number
    max_size       = number
    min_size       = number
    labels         = map(string)
    taints = list(object({
      key    = string
      value  = string
      effect = string
    }))
    tags = map(string)
  }))
}
```

## Environment Configuration

```hcl
# environments/production/main.tf

terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "production/main.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Environment = "production"
      ManagedBy   = "terraform"
      Project     = var.project_name
    }
  }
}

module "vpc" {
  source = "../../modules/vpc"

  name               = "${var.project_name}-production"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets    = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = false

  tags = var.tags
}

module "eks" {
  source = "../../modules/eks"

  cluster_name    = "${var.project_name}-production"
  cluster_version = "1.28"
  subnet_ids      = module.vpc.private_subnet_ids

  node_groups = {
    general = {
      instance_types = ["m6i.xlarge"]
      capacity_type  = "ON_DEMAND"
      disk_size      = 100
      desired_size   = 3
      max_size       = 10
      min_size       = 2
      labels         = { workload = "general" }
      taints         = []
      tags           = {}
    }
    spot = {
      instance_types = ["m6i.xlarge", "m5.xlarge"]
      capacity_type  = "SPOT"
      disk_size      = 50
      desired_size   = 2
      max_size       = 20
      min_size       = 0
      labels         = { workload = "batch" }
      taints = [{
        key    = "spot"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
      tags = {}
    }
  }

  tags = var.tags
}
```

## Locals and Data Sources

```hcl
# modules/vpc/locals.tf

locals {
  az_count = length(var.availability_zones)

  subnet_bits = ceil(log(local.az_count * 2, 2))

  public_subnet_cidrs = [
    for i in range(local.az_count) :
    cidrsubnet(var.cidr_block, local.subnet_bits, i)
  ]

  private_subnet_cidrs = [
    for i in range(local.az_count) :
    cidrsubnet(var.cidr_block, local.subnet_bits, i + local.az_count)
  ]

  common_tags = merge(
    var.tags,
    {
      Module    = "vpc"
      CreatedBy = "terraform"
    }
  )
}

# modules/vpc/data.tf

data "aws_region" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}
```
