from okular.db.models import Settings

def get_last_update_string():
    last_update = Settings.query.filter_by(name = 'last_update').first()
    last_update_str = '-'
    if not last_update is None:
        last_update_str = last_update.value
    return last_update_str
