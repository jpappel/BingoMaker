
# variables.tf

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  default     = "us-east-1"
}

variable "cognito_domain_prefix" {
  description = "The prefix for the Cognito domain"
  default     = "bingo-maker-cs399"
}

variable "s3_images_bucket_name" {
  description = "The S3 bucket to hold application assets"
  default     = "cs399-bingo-maker-images"
}

variable "s3_amplify_bucket_name" {
  description = "The S3 bucket to hold the html files"
  default     = "cs399-bingo-maker-app"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  default     = "BingoMaker"
}

variable "instance_profile_name" {
  description = "IAM instance profile name"
  default     = "LabInstanceProfile"
}