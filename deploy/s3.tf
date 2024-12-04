resource "aws_s3_bucket" "images_source" {
  bucket = var.s3_images_bucket_name
}

resource "aws_s3_bucket" "amplify_source" {
  bucket        = var.s3_amplify_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "amplify_source" {
  bucket              = aws_s3_bucket.amplify_source.id
  block_public_acls   = false
  block_public_policy = false
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
resource "aws_s3_object" "variables_js" {
  bucket       = aws_s3_bucket.amplify_source.bucket
  key          = "variables.js"
  content_type = "application/javascript"

  content = templatefile("../static/variables.js", {
    SERVER_IP  = "https://${aws_api_gateway_rest_api.bingo_maker_api.id}.execute-api.us-east-1.amazonaws.com/prod",
    COGNITO_IP = "https://${aws_cognito_user_pool_domain.bingo_maker.domain}.auth.us-east-1.amazoncognito.com"
  })
}

resource "null_resource" "upload_static_files" {
  provisioner "local-exec" {
    command = <<EOT
        aws s3 cp ../static/. s3://${aws_s3_bucket.amplify_source.bucket} --recursive --exclude "server_ip.js" 
    EOT
  }
  depends_on = [aws_s3_bucket.amplify_source]
}

