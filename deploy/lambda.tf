# Create a list of Python files in the directory (requires external data source)
data "local_file" "lambda_files" {
  for_each = fileset("../lambdas/", "*.py")

  filename = "../lambdas/${each.value}" # full path to the lambda file
}

data "aws_iam_role" "lab_role" {
  name = "LabRole"
}


resource "aws_lambda_function" "functions" {
  for_each = data.local_file.lambda_files

  function_name               = "${replace(each.key, ".py", "")}"
  handler                     = "lambda_handler"
  runtime                     = "python3.13"
  timeout                     = 5

  filename                    = "../lambdas/${each.key}.zip" 
  source_code_hash            = data.archive_file.function_zip[each.key].output_base64sha256

  role                        = data.aws_iam_role.lab_role.arn

  layers = [
    aws_lambda_layer_version.base_layer.arn,
    aws_lambda_layer_version.helper_layer.arn
  ]
}


resource "aws_lambda_layer_version" "helper_layer" {
    filename = "../layers/helper_layer/helper_layer.zip"
    layer_name = "helper_layer"
    compatible_runtimes = ["python3.13"]
}

resource "aws_lambda_layer_version" "base_layer" {
    filename = "../layers/base_layer/base_layer.zip"
    layer_name = "base_layer"
    compatible_runtimes = ["python3.13"]
}

# Archive each Python file into a zip
data "archive_file" "function_zip" {
  for_each = data.local_file.lambda_files

  source_file  = "../lambdas/${each.key}"  # Reference the function source dir
  type        = "zip"
  output_path = "../lambdas/${each.key}.zip" # Zipping each function folder
}

output "lambda_files" {
    value = data.local_file.lambda_files
}