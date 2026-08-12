# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled" # Desactivado para ahorro de costos en laboratorio
  }

  tags = local.common_tags
}

# ECS Task Definition (Fargate)
resource "aws_ecs_task_definition" "app" {
  family                   = "${local.name_prefix}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "web"
      image     = var.ghcr_image
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "DEBUG", value = "False" },
        { name = "USE_POSTGRES", value = "True" },
        { name = "USE_S3", value = "True" },
        { name = "DB_PORT", value = "5432" },
        { name = "AWS_STORAGE_BUCKET_NAME", value = aws_s3_bucket.media.id },
        { name = "AWS_S3_REGION_NAME", value = var.aws_region },
        { name = "SECURE_PROXY_SSL_HEADER", value = "True" },
        { name = "SECURE_SSL_REDIRECT", value = var.certificate_arn != "" ? "True" : "False" },
        { name = "SESSION_COOKIE_SECURE", value = var.certificate_arn != "" ? "True" : "False" },
        { name = "CSRF_COOKIE_SECURE", value = var.certificate_arn != "" ? "True" : "False" },
        { name = "CSRF_TRUSTED_ORIGINS", value = var.csrf_trusted_origins },
        { name = "ALLOWED_HOSTS", value = "*" }
      ]

      secrets = [
        { name = "SECRET_KEY", valueFrom = aws_ssm_parameter.secret_key.arn },
        { name = "DB_PASSWORD", valueFrom = aws_ssm_parameter.db_password.arn },
        { name = "DB_USER", valueFrom = aws_ssm_parameter.db_user.arn },
        { name = "DB_NAME", valueFrom = aws_ssm_parameter.db_name.arn },
        { name = "DB_HOST", valueFrom = aws_ssm_parameter.db_host.arn }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = local.common_tags
}

# ECS Service
resource "aws_ecs_service" "main" {
  name                               = "${local.name_prefix}-service"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.app.arn
  desired_count                      = var.ecs_desired_count
  launch_type                        = "FARGATE"
  health_check_grace_period_seconds = 60

  network_configuration {
    subnets          = var.enable_nat_gateway ? [aws_subnet.private_ecs_1.id, aws_subnet.private_ecs_2.id] : [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = var.enable_nat_gateway ? false : true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs.arn
    container_name   = "web"
    container_port   = var.container_port
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  depends_on = [
    aws_lb_listener.http,
    aws_db_instance.postgres
  ]

  tags = local.common_tags
}
