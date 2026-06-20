output "public_sg_id" {
  value = aws_security_group.public_sg.id

}

output "app_sg_id" {
  value = aws_security_group.app_sg.id

}

output "data_sg_id" {
  value = aws_security_group.data_sg.id

}
