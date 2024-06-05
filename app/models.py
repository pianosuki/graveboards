from app import db
from .utils import generate_token, aware_utcnow

__all__ = [
    "User",
    "ApiKey",
    "Beatmap",
    "BeatmapVersion",
    "Beatmapset",
    "Leaderboard",
    "Score"
]


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    scores = db.relationship("Score", backref="user", lazy=True)
    tokens = db.relationship("OauthToken", backref="user", lazy=True)


class ApiKey(db.Model):
    __tablename__ = "api_keys"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), unique=True, default=generate_token(32))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=aware_utcnow)


class OauthToken(db.Model):
    __tablename__ = "oauth_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)
    is_revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=aware_utcnow)


class Beatmap(db.Model):
    __tablename__ = "beatmaps"
    id = db.Column(db.Integer, primary_key=True)
    beatmapset_id = db.Column(db.Integer, db.ForeignKey("beatmapsets.id"), nullable=False)
    leaderboards = db.relationship("Leaderboard", backref="beatmap", lazy=True)
    versions = db.relationship("BeatmapVersion", backref="beatmap", lazy=True)


class BeatmapVersion(db.Model):
    __tablename__ = "beatmap_versions"
    id = db.Column(db.Integer, primary_key=True)
    beatmap_id = db.Column(db.Integer, db.ForeignKey("beatmaps.id"), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    difficulty_rating = db.Column(db.Float, nullable=False)
    mode = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    total_length = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    version = db.Column(db.String, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    ar = db.Column(db.Float, nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    convert = db.Column(db.Boolean, nullable=False)
    count_circles = db.Column(db.Integer, nullable=False)
    count_sliders = db.Column(db.Integer, nullable=False)
    count_spinners = db.Column(db.Integer, nullable=False)
    cs = db.Column(db.Float, nullable=False)
    deleted_at = db.Column(db.DateTime)
    drain = db.Column(db.Integer, nullable=False)
    hit_length = db.Column(db.Integer, nullable=False)
    is_scoreable = db.Column(db.Boolean, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    mode_int = db.Column(db.Integer, nullable=False)
    passcount = db.Column(db.Integer, nullable=False)
    playcount = db.Column(db.Integer, nullable=False)
    ranked = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)
    checksum = db.Column(db.String(32), unique=True, nullable=False)
    leaderboard = db.relationship("Leaderboard", uselist=False, lazy=True)


class Beatmapset(db.Model):
    __tablename__ = "beatmapsets"
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String, nullable=False)
    artist_unicode = db.Column(db.String, nullable=False)
    covers = db.Column(db.Text, nullable=False)
    creator = db.Column(db.String, nullable=False)
    favourite_count = db.Column(db.Integer, nullable=False)
    hype = db.Column(db.Integer)
    nsfw = db.Column(db.Boolean, nullable=False)
    offset = db.Column(db.Integer, nullable=False)
    play_count = db.Column(db.Integer, nullable=False)
    preview_url = db.Column(db.String, nullable=False)
    source = db.Column(db.String, nullable=False)
    spotlight = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    title_unicode = db.Column(db.String, nullable=False)
    track_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=False)
    video = db.Column(db.Boolean, nullable=False)
    beatmaps = db.relationship("Beatmap", backref="beatmapset", lazy=True)


class Leaderboard(db.Model):
    __tablename__ = "leaderboards"
    id = db.Column(db.Integer, primary_key=True)
    beatmap_id = db.Column(db.Integer, db.ForeignKey("beatmaps.id"), nullable=False)
    beatmap_version_id = db.Column(db.Integer, db.ForeignKey("beatmap_versions.id"), nullable=False)
    scores = db.relationship("Score", backref="leaderboard", lazy=True)


class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    beatmap_id = db.Column(db.Integer, db.ForeignKey("beatmaps.id"), nullable=False)
    beatmapset_id = db.Column(db.Integer, db.ForeignKey("beatmapsets.id"), nullable=False)
    leaderboard_id = db.Column(db.Integer, db.ForeignKey("leaderboards.id"), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    max_combo = db.Column(db.Integer, nullable=False)
    mode = db.Column(db.String, nullable=False)
    mode_int = db.Column(db.Integer, nullable=False)
    mods = db.Column(db.Text, nullable=False)
    perfect = db.Column(db.Boolean, nullable=False)
    pp = db.Column(db.Float)
    rank = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    statistics = db.Column(db.Text, nullable=False)
    type = db.Column(db.String, nullable=False)
