from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput,
)


from constructs import Construct

class CustomVPC(Construct):
    def __init__(self, scope: Construct, id: str, vpc_cidr: str, vpc_name: str, 
                 instance_type: str, ssh_allowed_ips: list, icmp_allowed_ips: list, 
                 public_subnet_cidrs: list, private_subnet_cidrs: int,
                 key_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC
        self.vpc = ec2.Vpc(
            self, f"{vpc_name}VPC",
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=public_subnet_cidrs
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=private_subnet_cidrs
                )
            ],
            nat_gateways=1,
            create_internet_gateway=True
        )

        # Create Security Group
        sg = ec2.SecurityGroup(
            self, f"{vpc_name}SG",
            vpc=self.vpc,
            description=f"Security group for {vpc_name} EC2 instance",
            allow_all_outbound=True
        )

        # Add ingress rules
        for ip in ssh_allowed_ips:
            sg.add_ingress_rule(
                ec2.Peer.ipv4(ip),
                ec2.Port.tcp(22),
                "Allow SSH access"
            )


        for ip in icmp_allowed_ips:
            sg.add_ingress_rule(
                ec2.Peer.ipv4(ip),
                ec2.Port.all_icmp(),
                "Allow ICMP access"
            )

        # Create IAM role for EC2
        # role = iam.Role(
        #     self, f"{vpc_name}EC2Role",
        #     assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        # )
        # role.add_managed_policy(
        #     iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        # )

        # Create EC2 instance
        self.instance = ec2.Instance(
            self, f"{vpc_name}EC2Instance",
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,
                availability_zones=["us-east-1a"]
            ),
            security_group=sg,
            # role=role,
            key_name= "my-key-pair",
            # associate_public_ip_address=True
        )


class NetworkingPocStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # Create a key pair
        key_pair = ec2.KeyPair(self, "MyKeyPair",
            key_pair_name="my-key-pair",
        )

        # Output the key pair name
        CfnOutput(self, "NetworkPOC-keypair",
            value=key_pair.key_pair_name,
            description="Name of the key pair"
        )

        # VPC configurations
        vpc_configs = [
            {
                "name": "A", 
                "cidr": "10.0.0.0/16",
                "public_subnet_cidrs": 24,
                "private_subnet_cidrs": 24,
                "ssh_allowed_ips": ["99.78.144.128/32", "15.248.2.76/32", "18.206.107.24/29"],
                "icmp_allowed_ips": ["10.1.0.0/16", "10.2.0.0/16"]
            },
            {
                "name": "B", 
                "cidr": "10.1.0.0/16",
                "public_subnet_cidrs": 24,
                "private_subnet_cidrs": 24,
                "ssh_allowed_ips": ["99.78.144.128/32", "15.248.2.76/32", "18.206.107.24/29"],
                "icmp_allowed_ips": ["10.0.0.0/16", "10.2.0.0/16"]
            },
            {
                "name": "C", 
                "cidr": "10.2.0.0/16",
                "public_subnet_cidrs": 24,
                "private_subnet_cidrs": 24,
                "ssh_allowed_ips": ["99.78.144.128/32", "15.248.2.76/32", "18.206.107.24/29"],
                "icmp_allowed_ips": ["10.0.0.0/16", "10.1.0.0/16"]
            }
        ]

       
        # Create VPCs and EC2 instances
        for config in vpc_configs:
            vpc = CustomVPC(
                self, f"VPC{config['name']}",
                vpc_cidr=config['cidr'],
                vpc_name=f"VPC{config['name']}",
                instance_type="t2.micro",
                ssh_allowed_ips=config['ssh_allowed_ips'],
                icmp_allowed_ips=config['icmp_allowed_ips'],
                public_subnet_cidrs=config['public_subnet_cidrs'],
                private_subnet_cidrs=config['private_subnet_cidrs'],
                key_name= key_pair.key_pair_name
            )

            CfnOutput(
                self, f"VPC{config['name']}ID",
                value=vpc.vpc.vpc_id,
                description=f"VPC {config['name']} ID"
            )

            CfnOutput(
                self, f"EC2Instance{config['name']}ID",
                value=vpc.instance.instance_id,
                description=f"EC2 Instance ID in VPC {config['name']}"
            )
