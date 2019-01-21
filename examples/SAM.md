# SAM Templates

These are templaces that can be used with [SAM](https://aws.amazon.com/serverless/sam/).

**Location:**

Project Root

**Content:**

Basic template that creates an API Gateway API with a Lambda Function

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
    ghi

    GitHub IRC Notification Service

Resources:
    LambdaFunction:
        Type: AWS::Serverless::Function
        Properties:
            FunctionName: ghi
            CodeUri: dist/
            Handler: index.handler
            Runtime: python3.6
            Timeout: 75
            Events:
                Ghi:
                    Type: Api
                    Properties:
                        Path: /
                        Method: ANY

Outputs:

    APIEndpoint:
        Description: "API endpoint"
        Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"

    FunctionArn:
        Description: "Lambda Function ARN"
        Value: !GetAtt LambdaFunction.Arn
```

---

Template using parameters stored in AWS SSM Parameter Store for secrets and custom domain.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
    ghi

    GitHub IRC Notification Service
    
Parameters:
    GitHubSecret:
        Type : 'AWS::SSM::Parameter::Value<String>'
        Default: /ghi-github-secret-gkrizek-repo1
    IRCSecret:
        Type : 'AWS::SSM::Parameter::Value<String>'
        Default: /ghi-irc-password-mypool
    Domain:
        Type: String
        Default: ghi.domain.com
    SSLCert:
        Type : String
        Default: arn:aws:acm:us-west-2:123456789123:certificate/52614373-0929-4dcc-5bcd-af7af95b6ea3

Resources:
    LambdaFunction:
        Type: AWS::Serverless::Function
        Properties:
            FunctionName: ghi
            CodeUri: dist/
            Handler: index.handler
            Runtime: python3.6
            Timeout: 75
            Environment: 
                Variables:
                    GHI_GITHUB_SECRET_GKRIZEK_REPO1: !Ref GitHubSecret
                    GHI_IRC_PASSWORD_MYPOOL: !Ref IRCSecret
            Events:
                Ghi:
                    Type: Api
                    Properties:
                        Path: /{proxy+}
                        Method: post


    APIDomainName:
        Type: AWS::ApiGateway::DomainName
        Properties:
            CertificateArn: !Ref SSLCert
            DomainName: !Ref Domain


    APIBasePathMapping:
        Type: AWS::ApiGateway::BasePathMapping
        DependsOn:
            - ServerlessRestApiProdStage
        Properties:
            DomainName: !Ref Domain
            RestApiId: !Ref ServerlessRestApi
            Stage: !Ref ServerlessRestApi.Stage


Outputs:

    APIEndpoint:
        Description: "API endpoint"
        Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"

    FunctionArn:
        Description: "Lambda Function ARN"
        Value: !GetAtt LambdaFunction.Arn
```