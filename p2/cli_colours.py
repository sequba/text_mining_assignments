def coloured(string, colour='g'):
    bold = '\033[1m'
    control = dict()
    control['w'] = '\033[0m'  # white (normal)
    control['r'] = '\033[31m' # red
    control['g'] = '\033[32m' # green
    control['o'] = '\033[33m' # orange
    control['b'] = '\033[34m' # blue
    control['p'] = '\033[35m' # purple
    return bold+control[colour]+string+control['w']
