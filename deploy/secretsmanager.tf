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