# EC2Bot

EC2Bot is a way to easily manage EC2 instances via Slack or with voice commands.

## Setup

1. Use AWS Lambda to create a function using the contents of the "ec2bot.py" file. The role associated with the function can use the the managed policy "AmazonEC2FullAccess" and the following role policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
```

2. Recreate the AWS Lex intents and slots using the "ec2bot.json" file.
