![ghi](images/ghi.png)

**G**it**H**ub **I**RC Notification Service

Ghi (pronounced 'ghee') is a relay between GitHub and IRC. It was created to take the place of the [now depreciated](https://developer.github.com/changes/2018-04-25-github-services-deprecation/) [GitHub IRC Service](https://github.com/github/github-services/blob/master/lib/services/irc.rb). Ghi receives events from GitHub for a specified repository via a webhook. Then it parses the event and sends the relevant information to your configured IRC channels. Ghi was written to be very configuration driven. Therefore, Ghi is set up with a `.ghi.yml` file and can listen for multiple repositories and send to multiple channels. Most of the features in the original GitHub Service are supported in Ghi as well.


# Getting Started

Ghi was designed and written to be ran in [AWS Lambda](https://aws.amazon.com/lambda/) with [API Gateway](https://aws.amazon.com/api-gateway/). However, I've also created a very simple HTTP server implementation so Ghi can be ran on any server if desired. Ghi is configured entirely with the `.ghi.yml` file. In this file you will set all necessary information including repositories, IRC nick, IRC host, channels, etc.

## Deployment

### AWS Lambda

Ghi was written to be ran in AWS Lambda and is the recommended deployment type. There are many ways to deploy Ghi to Lambda, I've found the simplest solution to be [SAM](https://aws.amazon.com/serverless/sam/). I've included several example SAM template in the [examples/SAM.md](examples/SAM.md) file. These can get you started running Ghi in Lambda quickly, but your own deployment method will work as well. If using your own process, be sure to create an API Gateway as well. During the build process be sure install the dependencies in the [`requirements-aws.txt`](requirements-aws.txt) file and add your `.ghi.yml` file. Below is the necessary information for running in Lambda:

- **runtime** - `python3.6`
- **handler** - `index.handler`
- **timeout** - `75 seconds`
- **memory** - `128 MB`

### Server

Ghi comes with a minimal HTTP server that can be used to run Ghi on a server if desired. If you need more advanced HTTP functionality like SSL, Error handling, load balancing, etc, you should use something like Nginx as a reverse proxy. To deploy, you can simply clone this repository or add Ghi to your existing deployment workflow. Ensure that during deployment you also bundle/install the dependencies in the [`requirements-server.txt`](requirements-server.txt) file and add your `.ghi.yml` file.

```
$ git clone https://github.com/gkrizek/ghi.git
$ cd ghi/
$ pip3 install -r requirements-server.txt
```

## Setting Configuration

### .ghi.yml

#### Location

The `.ghi.yml` file is what drives all the functionality of Ghi. When a request comes in, Ghi attempts to automatically find the `.ghi.yml` file from a list of common places in the filesystem. The directories it searches are (in order):

- Current Directory (`./`)
- Home Directory (`~/`)
- Temp Directory (`/tmp`)

You can also manually specify where the Ghi file is located with the `GH_CONFIG_PATH` environment variable. This will attempt to use the `.ghi.yml` file at the specified location regardless of any of the other file locations.

To explain, if I have a `~/.ghi.yml` file and a `./.ghi.yml` file in my current directory, Ghi will use the one in my current directory and ignore the one in my home directory. If I have `GH_CONFIG_PATH="~/configs/.ghi.yml"`, then it will try to use that file only and ignore any others. 

#### Contents

The Ghi file is where you specify things like repositories, branches, channels, IRC details, etc. Ghi uses something called a "Pool" to determine which events do what. A Pool can have 1 or more repositories and 1 or more channels. You can also list multiple pools in a single Ghi instance. So you could have both `gkrizek/repo1` and `gkrizek/repo2` sending messages to `#my-cool-channel` while also having `gkrizek/repo3` sending messages to `#other-cool-channel` and `#last-cool-channel` (and of course many more variations of that).

The top two required parameters of the Ghi file are `version` and `pools`. Currently there is only a version `1` of the Ghi file, but `pools` will be a list of Pool configurations. Each Pool is required to define some GitHub information like repository names and validation secrets. They will also need to specify IRC data like nick, host, password, and channels.

There are a lot more options that you can set to further configure Ghi. [See the Configuration section.](#configuration)

**Basic `.ghi.yml` Example:**

```yaml
version: 1
pools:
  - name: my-pool
    github:
      repos:
        - name: gkrizek/repo1
          secret: 3ccb8d36bd4c67dd1dffcff9ca2c40
    irc:
      host: chat.freenode.net
      nick: my-irc-bot
      channels:
        - my-cool-channel
```

_More Ghi file examples in [`examples/.ghi.yml.md`](examples/.ghi.yml.md)._

**Important Note:**

If you are running Ghi in AWS your IRC nick _must_ be registered with an email and password. This is because Freenode requires all nicks connecting from AWS to be registered first to cut down on spam.

### Environment Variable

Ghi allows for some configuration values to be set using environment variables. Primarily the values that are sensitive, such as the GitHub secret and IRC password.

To set the GitHub Secret with an environment variable rather than putting it in the `.ghi.yml` file, use the variable `GHI_GITHUB_SECRET_<OWNER>_<REPO>`. The `<OWNER>` and `<REPO>` are the owner and name of the repository with any special characters removed and all uppercase. So if you are trying to set a secret for repository `gkrizek/ci-pipeline_1` you would use `GHI_GITHUB_SECRET_GKRIZEK_CIPIPELINE1`.

To set the password for your IRC bot with an environment variable, use `GHI_IRC_PASSWORD_<NAME>`. The `<NAME>` is the name you gave your pool in the `.ghi.yml` file with any special characters removed and all uppercase. So if I gave my pool a name of `my-pool`, I would set the IRC password with `GHI_IRC_PASSWORD_MYPOOL`.

### GitHub

To configure GitHub to send events to your Ghi instance, you create a webhook in your repository. [Here is the GitHub documentation on how to do that](https://developer.github.com/webhooks/creating/). The Payload URL is whatever URL you have given your Ghi instance. _The path does not matter to Ghi_. Ghi does not check the path of the request and will respond to any path. The Content Type should be `application/json`. It is highly recommended to use a Secret for the webhook, but not required. You can then select whichever Event Types you want Ghi to act on, however [check that Ghi supports the event first.](#supported-event-types)

## Running

### AWS Lambda

After you have deployed your function to Lambda, there isn't much else needed for running Ghi. Simply make requests to the provisioned endpoint and API Gateway/Lambda will handle the rest. When running in Lambda, the default behavior is to respond to the request instantly, then process the event. This is because the GitHub webhook expects a response in less than 10 seconds to be considered healthy. To accomplish this, we re-invoke the same lambda function again to process the event, then respond to the intial request. If you would like Ghi to only respond when the request is complete, you can set the environment variable `GHI_LONG_RESPONSE="true"`. This will make Ghi appear as failing in GitHub, but should still be working properly. This could also be helpful for debugging.

**Important Note:**

If you are running Ghi in AWS your IRC nick _must_ be registered with an email and password. This is because Freenode requires all nicks connecting from AWS to be registered first to cut down on spam.

### Server

Once you have cloned or deployed Ghi to a server, you can run it by executing the [`ghi/server.py`](ghi/server.py) file. (Python 3 is required). This will start a web server listening on port `7890`. Ghi sends all logs to `stdout/stderr` so redirecting (`&>>`) to a log file is recommended. You can change the listener port with either the `--port` flag or the `GHI_PORT` environment variable. Because GitHub required webhooks to respond within 10 seconds, the Ghi web server executes the function then responds right away.

**Example:**

```
$ python3 ghi/server.py --port 8080
```

_Make sure your `PYTHONPATH` is set to your Ghi project directory._

I have [provided an example service file](examples/ghi.service.md) to use with systemd to make starting/stopping Ghi easier.

# Configuration

### .ghi.yml

Ghi is configurable and supports lots of combinations of repositories, channels, and pools. These are all possible configuration options and an example configuration with every value.

**Top Level**

| Name    | Default                            | Required | Description                      |
|:------- |:----------------------------------:|:--------:| --------------------------------:|
| version | 1                                  | Yes      | Version of the Ghi file          |
| debug   | False                              | No       | Enable/Disable Debug logging     |
| global  | Global Configuration Object        | No       | Set Global configuration options |
| pools   | List of Pool Configuration Objects | Yes      | Define all pool definitions      |

**Global Configuration Object**

| Name               | Default                                   | Required | Description                                          |
|:------------------ |:-----------------------------------------:|:--------:| ----------------------------------------------------:|
| github:shorten_url | False                                     | No       | Shorten all GitHub links with git.io                 |
| github:verify      | True                                      | No       | Verify the payload with the `X-Hub-Signature` header |
| irc:host           | None                                      | No       | Hostname for IRC Server                              |
| irc:port           | 6697 if SSL enabled, 6667 if SSL disabled | No       | Port for IRC Server                                  |
| irc:ssl            | True                                      | No       | Connect to IRC Server with SSL                       |
| irc:nick           | None                                      | No       | IRC Nickname                                         |
| irc:password       | None                                      | No       | IRC Password                                         |

**Pool Configuration Object**

| Name               | Default                                   | Required | Description                                          |
|:------------------ |:-----------------------------------------:|:--------:| ----------------------------------------------------:|
| name               | None                                      | Yes      | Name of the Pool                                     |
| github:repos       | None                                      | Yes      | List of Repository Configuration Objects             |
| github:shorten_url | False                                     | No       | Shorten all GitHub links with git.io                 |
| irc:host           | None                                      | Yes      | Hostname for IRC Server                              |
| irc:port           | 6697 if SSL enabled, 6667 if SSL disabled | No       | Port for IRC Server                                  |
| irc:ssl            | True                                      | No       | Connect to IRC Server with SSL                       |
| irc:nick           | None                                      | Yes      | IRC Nickname                                         |
| irc:password       | None                                      | No       | IRC Password                                         |
| irc:channels       | None                                      | Yes      | List of channels to send messages to                 |

**Repository Configuration Object**

| Name     | Default      | Required | Description                                              |
|:-------- |:------------:|:--------:| --------------------------------------------------------:|
| name     | None         | Yes      | Owner and name of the repository. Ex: `gkrizek/repo1`    |
| secret   | None         | No       | Secret you created with the webhook to validate payloads |
| branches | All branches | No       | List of branches in the repository to send messages for  |
| verify   | True         | No       | Verify the payload with the `X-Hub-Signature` header     |


**Example Configuration File**

```yaml
version: 1 # required
debug: true # optional, default False
global: # optional
    github: # optional
      shorten_url: true # optional, defaults to false
      verify: true # optional, defaults to true
    irc: # optional
      host: chat.freenode.net # optional
      port: 6697 # optional, default is 6697 for ssl and 6667 for non-ssl
      ssl: true # optional, default is true
      nick: my-irc-bot # optional, but must be set in pool if not here
      password: abc123 # optional, but must be set in pool if not here and needed

pools: # required
  - name: my-pool # required
    github: # required
      repos: # required
        - name: gkrizek/repo1 # at least 1 repo is required
          secret: 3ccb8d36bd4c67dd1dffcff9ca2c40 # optional, but if it's needed it must be set here or with environment variable
          branches: # optional, default is 'all'
            - master
            - staging
          verify: true # optional, default is true
      shorten_url: true # optional, defaults to false
    irc: # required
      host: chat.freenode.net # required
      port: 6697 # optional, default is 6697 for ssl and 6667 for non-ssl
      ssl: true # optional default is true
      nick: my-irc-bot # required
      password: abc123 # optional, but if it's required by the nick it must be set here or with environment variable
      channels: # required
        - my-cool-channel # at least 1 channel is required
```

If you define a parameter in the Global section and in your pool, the value in the pool will be used.

[See the `examples`directory for `.ghi.yml` examples, as well as others.](examples/)

**Important Note:**

If you are running Ghi in AWS your IRC nick _must_ be registered with an email and password. This is because Freenode requires all nicks connecting from AWS to be registered first to cut down on spam.


### Environment Variable

Some parameters are able to be exported as environment variables instead of being set in the Ghi file. These are all possible environment variables you can use.

| Name                               | Description                                              |
|:---------------------------------- | --------------------------------------------------------:|
| `GH_CONFIG_PATH`                   | Specify where the `.ghi.yml` file is.|
| `GHI_GITHUB_SECRET_<OWNER>_<REPO>` | Secret used to validate GitHub payloads. `<OWNER>` is repo owner in all caps with special characters removed. `<REPO>` is repository name in all caps with special characters removed. |
| `GHI_IRC_PASSWORD_<NAME>`          | Password for the IRC bot for a given pool. `<NAME>` is the name of the pool in the `.ghi.yml` file. |
| `GHI_LONG_RESPONSE`                | Only used in AWS. Don't respond until the request is complete instead of replying right away. |
| `GHI_PORT`                         | Only used in server. Specifies which port to listen on. |

### Supported Event Types

- [`push`](https://developer.github.com/v3/activity/events/types/#pushevent)
- [`pull_request`](https://developer.github.com/v3/activity/events/types/#pullrequestevent)