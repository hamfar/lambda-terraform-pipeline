
terraform {
  backend "s3" {
    bucket = "100.terraform.state"
    key    = "lambda-terraform-pipeline"
    region = "eu-west-1"
  }
}
resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "test_lambda" {
  filename      = "lambda_function_payload.zip"
  function_name = "lambda_function_name"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "index.test"
  runtime       = "python3.9"

  ephemeral_storage {
    size = 10240 # Min 512 MB and the Max 10240 MB
  }
}