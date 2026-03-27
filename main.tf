provider "random" {}

resource "random_string" "example" {
  length  = 16
  special = false
}


provider "archive" {}

data "archive_file" "example" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "example.zip"
  depends_on = [
    local_file.example
  ]
}

provider "local" {}

resource "local_file" "example" {
  content  = random_string.example.result
  filename = "${var.source_dir}/random_string.txt"
}