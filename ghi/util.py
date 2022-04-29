def matrix_html(msg):
    '''
    Escape text for matrix HTML.
    '''
    # This should be html.escape. however, the Matrix→IRC bridge currently eats
    # everything that looks like HTML, even escaped. So go for a solution that
    # works for our particular case: simply strip characters that the bridge
    # has difficulty with (escaped and unescaped).
    # See https://github.com/matrix-org/matrix-appservice-irc/issues/1562.
    return msg.replace('<', '').replace('>', '').replace('&lt;', '').replace('&gt;', '')
