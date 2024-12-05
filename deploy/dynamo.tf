
# DynamoDB Table
resource "aws_dynamodb_table" "bingo_maker" {
  name         = var.dynamodb_table_name
  hash_key     = "id"
  billing_mode = "PROVISIONED"

  attribute {
    name = "id"
    type = "S"
  }

  read_capacity  = 1
  write_capacity = 1
}
