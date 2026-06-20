provider "aws" {
  region  = "eu-central-1"
  profile = "default"
}

module "vpc" {
  source     = "./modules/vpc"
  cidr_block = "10.1.0.0/16"
}


module "subnets" {
  source = "./modules/subnets"
  vpc_id = module.vpc.vpc_id
}

module "routing" {
  source = "./modules/routing"

  vpc_id            = module.vpc.vpc_id
  igw_id            = module.vpc.igw_id
  public_subnet_id  = module.subnets.public_subnet_id
  private_subnet_id = module.subnets.private_subnet_id
  nat_gateway_id    = module.routing.nat_gateway_id
}

module "security_groups" {
  source = "./modules/security_groups"
  vpc_id = module.vpc.vpc_id
}
