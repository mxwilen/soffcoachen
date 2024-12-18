class StoredTeams:
    """Singleton-like store for teams."""
    _teams = []

    @classmethod
    def set_teams(self, teams):
        self._teams = teams

    @classmethod
    def _get_teams(self):
        """Get the list of preloaded teams."""
        return self._teams
    
def get_teams():
    return StoredTeams._get_teams

def get_tags():
    """Return the preloaded tags from app config."""
    return ["transfers & truppbygge", "matcher", "kultur", "förening", "övrigt"]
