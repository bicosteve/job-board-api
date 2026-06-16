provider "aws" {
  region = "eu-central-1"
}

module "vpc" {
  source     = "./module/vpc"
  cidr_block = "10.1.0.0/16"
}


module "subnets" {
  source = "./module/subnets"
  vpc_id = module.vpc.vpc_id
}

module "security_groups" {
  source = "./modules/security_groups"
  vpc_id = module.vpc.vpc_id
}
