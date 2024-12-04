
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

