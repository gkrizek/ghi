import hmac
from hashlib import sha1


def validatePayload(payload, signature, secret):

    # GitHub sends a signature of the payload created from a secret you provide
    # This checks to make sure the payload matches the signature sent from GitHub
    # https://developer.github.com/webhooks/securing/#validating-payloads-from-github

    print(secret)
    print(signature)
    print(payload)

    payload = payload.encode('utf-8')
    secret = secret.encode('utf-8')
    generatedSignature = 'sha1=' + hmac.new(secret, payload, sha1).hexdigest()
    print(generatedSignature)
    identicalSignatures = hmac.compare_digest(signature, generatedSignature)
    print(identicalSignatures)
    return identicalSignatures