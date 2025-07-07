def parse_log(path):
    log_entries = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(' ')
            timestamp = parts[0].replace('T', ' ')
            rest = ' '.join(parts[1:])
            log_entries.append({
                'timestamp': timestamp,
                'content': rest
            })
    return log_entries
