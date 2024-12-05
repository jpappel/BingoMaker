resource "aws_api_gateway_rest_api" "bingo_maker_api" {
  name        = "BingoMakerAPI"
  description = "API for managing Bingo Maker tile pools and cards"
  body        = templatefile("../api-template.yaml", {
    lab-role-arn = data.aws_iam_role.lab_role.arn,
    tilepools-get-function-arn = aws_lambda_function.functions["get_tilepools.py"].arn,
    tilepools-post-function-arn = aws_lambda_function.functions["new_tilepool.py"].arn,
    tilepool-get-by-id-function-arn = aws_lambda_function.functions["get_tilepool.py"].arn,
    tilepool-patch-by-id-function-arn = aws_lambda_function.functions["update_tilepool.py"].arn,
    tilepool-delete-by-id-function-arn = aws_lambda_function.functions["delete_tilepool.py"].arn,
    bingocard-get-by-id-function-arn = aws_lambda_function.functions["new_bingocard.py"].arn
  })
  depends_on = [aws_lambda_function.functions]
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.bingo_maker_api.id
  stage_name  = "prod"
}
