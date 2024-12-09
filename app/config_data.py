from flask import current_app as app

def get_teams():
    """Return the preloaded teams from app config."""
    return ["transfers & truppbygge", "matcher", "kultur", "förening", "övrigt"]

def get_tags():
    """Return the preloaded tags from app config."""
    return ["transfers & truppbygge", "matcher", "kultur", "förening", "övrigt"]