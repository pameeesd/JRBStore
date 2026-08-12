# Parámetros Sensibles Cifrados en SSM Parameter Store (SecureString / KMS Default Key)
resource "aws_ssm_parameter" "secret_key" {
  name        = "/${var.project_name}/${var.environment}/SECRET_KEY"
  description = "SECRET_KEY criptografica de producción para Django"
  type        = "SecureString"
  value       = var.secret_key

  tags = local.common_tags
}

resource "aws_ssm_parameter" "db_password" {
  name        = "/${var.project_name}/${var.environment}/DB_PASSWORD"
  description = "Contraseña de la base de datos PostgreSQL de producción"
  type        = "SecureString"
  value       = var.db_password

  tags = local.common_tags
}

resource "aws_ssm_parameter" "db_user" {
  name        = "/${var.project_name}/${var.environment}/DB_USER"
  description = "Usuario de la base de datos PostgreSQL"
  type        = "String"
  value       = var.db_username

  tags = local.common_tags
}

resource "aws_ssm_parameter" "db_name" {
  name        = "/${var.project_name}/${var.environment}/DB_NAME"
  description = "Nombre de la base de datos PostgreSQL"
  type        = "String"
  value       = var.db_name

  tags = local.common_tags
}

resource "aws_ssm_parameter" "db_host" {
  name        = "/${var.project_name}/${var.environment}/DB_HOST"
  description = "Hostname del endpoint de RDS PostgreSQL"
  type        = "String"
  value       = aws_db_instance.postgres.address

  tags = local.common_tags
}
