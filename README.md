![ghi](images/ghi.png)

**G**it**H**ub **I**RC Notification Service

Ghi (pronounced 'ghee') is a relay between GitHub and IRC. It was created to take the place of the [now depreciated](https://developer.github.com/changes/2018-04-25-github-services-deprecation/) [GitHub IRC Service](https://github.com/github/github-services/blob/master/lib/services/irc.rb). Ghi receives events from GitHub for a configured repository via a webhook. Then it parses the event and sends the relevant information to your configured IRC channels. Ghi was written to be very configuration driven. Therefore, Ghi is configured with a `.ghi.yml` file and can listen for multiple repositories and send to multiple channels. Most of the features in the original GitHub Service are supported in Ghi as well.


# Getting Started

Ghi was designed and written to be ran in [AWS Lambda](https://aws.amazon.com/lambda/) with [API Gateway](https://aws.amazon.com/api-gateway/). However, I've also created a very simple HTTP server implimentation so Ghi can be ran on any server if desired. Ghi is configured entirely with the `.ghi.yml` file. In this file you will set all necessary information including repositories, IRC nick, IRC host, channels, etc.

## Setting Configuration

### .ghi.yml

#### Location

The `.ghi.yml` file is what drives all the functionality of Ghi. When a request comes in, Ghi attempts to automatically find the `.ghi.yml` file from a list of common places in the filesystem. The directories it looks in are (in order):

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

### Environment Variable

Ghi allows for some configuration values to be set using Environment Variables. 

### GitHub

text

## Deployment

### AWS Lambda

text

### Server

text

## Running

### AWS Lambda

text

### Server

text


# Configuration

### .ghi.yml

text

### Environment Variable

text


# Contributors

- [Graham Krizek](https://github.com/gkrizek)



