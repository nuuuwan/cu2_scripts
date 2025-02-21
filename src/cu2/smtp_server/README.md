# SMTP Server Setup Script

## What is an SMTP Server?

An SMTP (Simple Mail Transfer Protocol) server is a mail server that handles the sending, receiving, and relaying of email messages. It uses the SMTP protocol to communicate with other mail servers and email clients. SMTP servers are essential for sending out emails from your domain and ensuring that they are delivered to the recipient's mail server.

## Prerequisites

- An AWS account
- AWS CLI configured with your credentials
- An EC2 instance running Amazon Linux 2
- A PEM file for SSH access to the EC2 instance

## Setup and Launch AWS Instance

1. **Create an AWS Account**: If you don't already have an AWS account, create one at [AWS Signup](https://aws.amazon.com/).

2. **Launch an EC2 Instance**:
   - Log in to the AWS Management Console.
   - Navigate to the EC2 Dashboard.
   - Click the "Launch Instance" button.
   - Choose an Amazon Machine Image (AMI). For example, select "Amazon Linux 2 AMI".
   - Choose an Instance Type. For example, select "t2.micro" (eligible for the free tier).
   - Configure Security Group. Create a new security group or select an existing one. Ensure the following rules are added:
     - SSH (port 22) from your IP address.
     - SMTP (port 25) from your IP address or any IP address if you want it to be publicly accessible.
   - Review and Launch. Review your settings and click "Launch".

3. **Connect to Your EC2 Instance**:
   - Open a terminal on your local machine.
   - Change permissions for the PEM file:
     ```sh
     chmod 400 /path/to/your-key-pair.pem
     ```
   - Connect to the instance:
     ```sh
     ssh -i /path/to/your-key-pair.pem ec2-user@your-instance-public-ip
     ```
     Replace `/path/to/your-key-pair.pem` with the path to your PEM file and `your-instance-public-ip` with the public IP address of your EC2 instance.

## Finding Parameters for `get_user_inputs`

To run the script, you will need to provide several parameters. Here is how to find them:

1. **AWS Access Key and Secret Key**:
   - These are your AWS credentials. You can create or find them in the AWS Management Console.
   - Navigate to the IAM Dashboard.
   - Click on "Users" and select your user.
   - Go to the "Security credentials" tab.
   - Under "Access keys", you can create a new access key or use an existing one.

2. **AWS Instance ID**:
   - This is the ID of your EC2 instance.
   - Navigate to the EC2 Dashboard.
   - Click on "Instances" in the left-hand menu.
   - Find your instance in the list and note the "Instance ID".

3. **PEM File Path**:
   - This is the path to the PEM file you downloaded when you created your EC2 instance.
   - Ensure the file has the correct permissions:
     ```sh
     chmod 400 /path/to/your-key-pair.pem
     ```

4. **SMTP Port**:
   - The default SMTP port is 25. You can use this or specify a different port if needed.

5. **Hostname**:
   - The hostname for your SMTP server. The default is "localhost".

6. **Domain**:
   - The domain for your SMTP server. The default is "localdomain".

7. **Mydestination**:
   - The destination domains for your SMTP server. The default is "$myhostname, localhost.$mydomain, localhost".

By providing these parameters, you will be able to run the script and set up your SMTP server on the AWS EC2 instance.

