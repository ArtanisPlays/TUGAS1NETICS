output "random_string" {
  description = "String acak yang dihasilkan"
  value       = random_string.example.result
}

output "archive_file_path" {
  description = "Path dari file arsip yang dihasilkan"
  value       = data.archive_file.example.output_path
}

output "local_file_path" {
  description = "Path dari file lokal yang dibuat"
  value       = local_file.example.filename
}