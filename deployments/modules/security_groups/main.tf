# Public SG: allow HTTP, HTTPS, SSH
resource "aws_security_group" "public_sg" {
  vpc_id = var.vpc_id
  name   = "public-SG"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80

    protocol = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443

    protocol = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    # we will use key-pair to access this!
    description = "Allow SSH ingress"
    from_port   = 22
    to_port     = 22

    protocol = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# App SG: Allows SSH from public instances
resource "aws_security_group" "app_sg" {
  vpc_id = var.vpc_id
  name   = "app-SG"


  ingress {
    description     = "SSH from public hosts"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.public_sg.id]
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

# Data SG : Allows access to data instances mysql, redis, rabbitmq
resource "aws_security_group" "data_sg" {
  vpc_id = var.vpc_id
  name   = "data-SG"


  ingress {
    description = "MySQL ingress"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    security_groups = [
      aws_security_group.public_sg.id,
      aws_security_group.app_sg.id,
    ]
  }

  ingress {
    description = "RabbitMQ ingress rules"
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    security_groups = [
      aws_security_group.public_sg.id,
      aws_security_group.app_sg.id,
    ]
  }

  ingress {
    description = "RabbitMQ UI"
    from_port   = 15672
    to_port     = 15672
    protocol    = "tcp"
    security_groups = [
      aws_security_group.public_sg.id
    ]
  }


  ingress {
    description = "Redis ingress rules"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    security_groups = [
      aws_security_group.public_sg.id,
      aws_security_group.app_sg.id,
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}


