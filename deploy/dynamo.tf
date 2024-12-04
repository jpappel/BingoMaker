
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
