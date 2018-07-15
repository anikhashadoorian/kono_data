import hashlib


def generate_invite_key(dataset):
    hash_str = f'{dataset.created_at}, {dataset.id}'
    hash_object = hashlib.sha256(str.encode(hash_str))
    invite_key = hash_object.hexdigest()
    return invite_key
