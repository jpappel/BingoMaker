# main.tf

# VPC and Subnet
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

# Security Group
resource "aws_security_group" "bingo_maker" {
  name        = "bingo-maker-ec2"
  description = "Allow http/https, ssh access"
  vpc_id      = aws_vpc.main.id
  # ingress rules
}

# EC2 Instance
resource "aws_instance" "bingo_maker_instance" {
  ami                         = "ami-06b21ccaeff8cd686"
  instance_type               = "t2.micro"
  key_name                    = "vockey"
  subnet_id                   = aws_subnet.main.id
  vpc_security_group_ids      = [aws_security_group.bingo_maker.id]
  associate_public_ip_address = true
  iam_instance_profile        = "LabInstanceProfile"
  user_data                   = file("./userdata.sh")

  tags = {
    Name = "bingo-maker"
  }
}