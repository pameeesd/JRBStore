# Security Group para el Application Load Balancer (ALB)
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Permite trafico HTTP/HTTPS entrante hacia el ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP desde Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS desde Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Envio de trafico hacia ECS Fargate en puerto 8000"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "${local.name_prefix}-alb-sg"
  }
}

# Security Group para ECS Fargate Tasks
resource "aws_security_group" "ecs" {
  name        = "${local.name_prefix}-ecs-sg"
  description = "Permite trafico unicamente desde el ALB hacia ECS Fargate"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Trafico entrante desde el Security Group del ALB"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Permite todo el trafico saliente (GHCR, S3, SSM, CloudWatch)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-ecs-sg"
  }
}

# Security Group para AWS RDS PostgreSQL
resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds-sg"
  description = "Permite trafico PostgreSQL unicamente desde las tareas de ECS"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Acceso PostgreSQL 5432 desde el Security Group de ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = {
    Name = "${local.name_prefix}-rds-sg"
  }
}
