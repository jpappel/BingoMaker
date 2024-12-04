resource "aws_api_gateway_rest_api" "bingo_maker_api" {
  name        = "BingoMakerAPI"
  description = "API for managing Bingo Maker tile pools and cards"
  body        = file("../api.yaml") # Path to your OpenAPI spec
}