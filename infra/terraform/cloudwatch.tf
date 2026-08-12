# Log Group Centralizado en CloudWatch para ECS Fargate
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = var.cloudwatch_retention_days

  tags = local.common_tags
}
