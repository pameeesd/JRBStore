variable "aws_region" {
  type        = string
  description = "Región de AWS donde se aprovisionará la infraestructura"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Nombre del proyecto utilizado para nombrar recursos"
  default     = "jrbstore"
}

variable "environment" {
  type        = string
  description = "Entorno de despliegue (production, staging, dev)"
  default     = "production"
}

variable "vpc_cidr" {
  type        = string
  description = "Bloque CIDR principal para la VPC"
  default     = "10.0.0.0/16"
}

variable "db_name" {
  type        = string
  description = "Nombre de la base de datos PostgreSQL"
  default     = "jrbstore"
}

variable "db_username" {
  type        = string
  description = "Nombre de usuario administrador de PostgreSQL"
  default     = "postgres"
}

variable "db_password" {
  type        = string
  description = "Contraseña de la base de datos PostgreSQL (Sensible, inyectar vía tfvars o env var)"
  sensitive   = true
  default     = "change-me-in-production-secure-pass"
}

variable "db_instance_class" {
  type        = string
  description = "Clase de instancia para AWS RDS PostgreSQL"
  default     = "db.t4g.micro"
}

variable "ecs_cpu" {
  type        = number
  description = "Unidades de CPU para la tarea de ECS Fargate (256 = 0.25 vCPU)"
  default     = 256
}

variable "ecs_memory" {
  type        = number
  description = "Memoria RAM en MB para la tarea de ECS Fargate"
  default     = 512
}

variable "ecs_desired_count" {
  type        = number
  description = "Número deseado de réplicas de la tarea de ECS Fargate"
  default     = 1
}

variable "container_port" {
  type        = number
  description = "Puerto en el que escucha la aplicación Django/Gunicorn dentro del contenedor"
  default     = 8000
}

variable "ghcr_image" {
  type        = string
  description = "Ruta de la imagen Docker de JRBStore publicada en GHCR (ej. ghcr.io/pameeesd/jrbstore:sha-1de1278)"
  default     = "ghcr.io/pameeesd/jrbstore:sha-1de1278"
}

variable "certificate_arn" {
  type        = string
  description = "ARN opcional de un certificado SSL/TLS emitido por AWS ACM para HTTPS"
  default     = ""
}

variable "csrf_trusted_origins" {
  type        = string
  description = "Cadena de orígenes confiables para CSRF separados por comas"
  default     = "https://jrbstore.example.com"
}

variable "secret_key" {
  type        = string
  description = "SECRET_KEY criptográfica de producción para Django (Sensible)"
  sensitive   = true
  default     = "change-me-in-production-django-secret-key-12345"
}

variable "cloudwatch_retention_days" {
  type        = number
  description = "Días de retención para los logs de CloudWatch"
  default     = 7
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Activar NAT Gateway para subnets privadas. Si es false, ECS Fargate utilizará asignación de IP pública para Pull de GHCR y ahorro de costos"
  default     = false
}
