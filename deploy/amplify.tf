resource "aws_amplify_app" "amplify_app" {
  name = "BingoMaker"
}

resource "aws_amplify_branch" "amplify_branch" {
  app_id      = aws_amplify_app.amplify_app.id
  branch_name = "main"
  description = "Main branch"
}