output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs de las subnets públicas"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_ecs_subnet_ids" {
  description = "IDs de las subnets privadas de cómputo ECS"
  value       = [aws_subnet.private_ecs_1.id, aws_subnet.private_ecs_2.id]
}

output "db_endpoint" {
  description = "Endpoint DNS de la base de datos AWS RDS PostgreSQL"
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "Puerto de conexión de la base de datos RDS PostgreSQL"
  value       = aws_db_instance.postgres.port
}

output "s3_bucket_name" {
  description = "Nombre del bucket S3 creado para almacenamiento media"
  value       = aws_s3_bucket.media.id
}

output "ecs_cluster_name" {
  description = "Nombre del cluster ECS Fargate"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Nombre del servicio ECS Fargate"
  value       = aws_ecs_service.main.name
}

output "alb_dns_name" {
  description = "Nombre DNS público del Application Load Balancer (ALB)"
  value       = aws_lb.main.dns_name
}

output "cloudwatch_log_group" {
  description = "Nombre del Log Group centralizado en CloudWatch"
  value       = aws_cloudwatch_log_group.ecs.name
}
