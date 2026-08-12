# VPC Principal
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${local.name_prefix}-vpc"
  }
}

# Internet Gateway para Subnets Públicas
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_prefix}-igw"
  }
}

# Subnets Públicas (Para ALB)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.name_prefix}-public-subnet-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.name_prefix}-public-subnet-2"
  }
}

# Subnets Privadas para ECS Cómputo
resource "aws_subnet" "private_ecs_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${local.name_prefix}-private-ecs-subnet-1"
  }
}

resource "aws_subnet" "private_ecs_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "${local.name_prefix}-private-ecs-subnet-2"
  }
}

# Subnets Privadas para RDS PostgreSQL Base de Datos
resource "aws_subnet" "private_db_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${local.name_prefix}-private-db-subnet-1"
  }
}

resource "aws_subnet" "private_db_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.21.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "${local.name_prefix}-private-db-subnet-2"
  }
}

# Route Table Pública
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${local.name_prefix}-public-rt"
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway Opcional para Ahorro de Costos en Laboratorio
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = {
    Name = "${local.name_prefix}-nat-eip"
  }
}

resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public_1.id

  tags = {
    Name = "${local.name_prefix}-nat-gw"
  }

  depends_on = [aws_internet_gateway.igw]
}

# Route Table Privada
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.nat[0].id
    }
  }

  tags = {
    Name = "${local.name_prefix}-private-rt"
  }
}

resource "aws_route_table_association" "private_ecs_1" {
  subnet_id      = aws_subnet.private_ecs_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_ecs_2" {
  subnet_id      = aws_subnet.private_ecs_2.id
  route_table_id = aws_route_table.private.id
}

# RDS DB Subnet Group (Subnets Privadas de Datos)
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = [aws_subnet.private_db_1.id, aws_subnet.private_db_2.id]

  tags = {
    Name = "${local.name_prefix}-db-subnet-group"
  }
}
