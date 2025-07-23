def master_message(msg_name, params={}):
    with open(f"entites/master_messages/{msg_name}.txt", 'r', encoding='utf-8') as file:
        msg = file.read()

    for k, v in params.items():
        msg = msg.replace(k, v)
    return msg
