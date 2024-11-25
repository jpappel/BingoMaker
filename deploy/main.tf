# main.tf

# VPC and Subnet
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

# Security Group
resource "aws_security_group" "bingo_maker" {
  name        = "bingo-maker-ec2"
  description = "Allow http/https, ssh access"
  vpc_id      = aws_vpc.main.id
  # ingress rules
}

# EC2 Instance
resource "aws_instance" "bingo_maker_instance" {
  ami                         = "ami-06b21ccaeff8cd686"
  instance_type               = "t2.micro"
  key_name                    = "vockey"
  subnet_id                   = aws_subnet.main.id
  vpc_security_group_ids      = [aws_security_group.bingo_maker.id]
  associate_public_ip_address = true
  iam_instance_profile        = "LabInstanceProfile"
  user_data                   = file("./userdata.sh")

  tags = {
    Name = "bingo-maker"
  }
}

resource "aws_s3_bucket" "images_source" {
    bucket = var.s3_images_bucket_name
}


# DynamoDB Table
resource "aws_dynamodb_table" "bingo_maker" {
  name         = "BingoMaker"
  hash_key     = "id"
  billing_mode = "PROVISIONED"

  attribute {
    name = "id"
    type = "S"
  }

  read_capacity  = 1
  write_capacity = 1
}


resource "aws_s3_bucket" "amplify_source" {
  bucket        = var.s3_amplify_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "amplify_source" {
  bucket                  = aws_s3_bucket.amplify_source.id
  block_public_acls       = false
  block_public_policy     = false
}

resource "aws_s3_bucket_policy" "amplify_source" {
  bucket     = aws_s3_bucket.amplify_source.id
  policy     = data.aws_iam_policy_document.amplify_source.json
  depends_on = [aws_s3_bucket_public_access_block.amplify_source]
}

data "aws_iam_policy_document" "amplify_source" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    } 

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.amplify_source.arn,
      "${aws_s3_bucket.amplify_source.arn}/*",
    ]
  }
}

resource "null_resource" "upload_static_files" {
  provisioner "local-exec" {
    command  = "aws s3 cp ../src/app/static s3://${aws_s3_bucket.amplify_source.bucket} --recursive && aws s3 cp ../src/app/templates s3://${aws_s3_bucket.amplify_source.bucket} --recursive"
  }
  depends_on = [aws_s3_bucket.amplify_source]
}

resource "aws_amplify_app" "amplify_app" {
    name = "BingoMaker"
}

resource "aws_amplify_branch" "amplify_branch" {
    app_id      = aws_amplify_app.amplify_app.id
    branch_name = "main"
    description = "Main branch"
}

# Cognito User Pool
resource "aws_cognito_user_pool" "bingo_maker" {
  name = "BingoMaker"

  password_policy {
    minimum_length    = 8
    require_uppercase = true
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
  }

  # Schema configuration
  schema {
    name                = "email" 
    attribute_data_type = "String"
    mutable             = true
    required            = true
  }
}

resource "aws_cognito_user_pool_client" "bingo_maker" {
  name                                 = "amplify"
  user_pool_id                         = aws_cognito_user_pool.bingo_maker.id
  explicit_auth_flows                  = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  supported_identity_providers         = ["COGNITO"]
  callback_urls                        = ["https://main.${aws_amplify_app.amplify_app.id}.amplifyapp.com/postlogin"]
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  generate_secret                      = true
}

# Cognito Domain
resource "aws_cognito_user_pool_domain" "bingo_maker" {
  domain       = var.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.bingo_maker.id
}

resource "aws_secretsmanager_secret" "cognito_user_pool_client_secret" {
  name                    = "CognitoUserPoolClientSecret"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "cognito_user_pool_client_secret" {
  secret_id     = aws_secretsmanager_secret.cognito_user_pool_client_secret.id
  secret_string = aws_cognito_user_pool_client.bingo_maker.client_secret
}


resource "aws_secretsmanager_secret" "cognito_user_pool_client_id" {
  name                    = "CognitoUserPoolClientId"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "cognito_user_pool_client_id" {
  secret_id     = aws_secretsmanager_secret.cognito_user_pool_client_id.id
  secret_string = aws_cognito_user_pool_client.bingo_maker.id
}


resource "aws_secretsmanager_secret" "cognito_user_pool_id" {
  name                    = "CognitoUserPoolId"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "cognito_user_pool_id" {
  secret_id     = aws_secretsmanager_secret.cognito_user_pool_id.id
  secret_string = aws_cognito_user_pool.bingo_maker.id
}

output "instance_id" {
  value = aws_instance.bingo_maker_instance.id
}

output "amplify_app_id" {
  value = aws_amplify_app.amplify_app.id
}