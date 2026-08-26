# Instancia RDS PostgreSQL en Subnets Privadas
resource "aws_db_instance" "postgres" {
  identifier        = "${local.name_prefix}-postgres"
  engine            = "postgres"
  engine_version    = "16.3"
  instance_class    = var.db_instance_class
  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false

  skip_final_snapshot     = true
  backup_retention_period = 1

  tags = local.common_tags
}
