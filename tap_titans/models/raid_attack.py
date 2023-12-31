from datetime import datetime

from tap_titans.models import model_type
from tap_titans.models.player import Player
from tap_titans.models.code import ClanCode, PlayerCode
from tap_titans.utils.base import BaseModel


class RaidAttackRaidStateCurrentPart(BaseModel):
    part_id: model_type.TitanPart
    current_hp: int


class RaidAttackRaidStateCurrent(BaseModel):
    current_hp: int
    enemy_id: model_type.Enemy
    parts: tuple[RaidAttackRaidStateCurrentPart, ...]


class RaidAttackRaidState(BaseModel):
    titan_index: int
    current: RaidAttackRaidStateCurrent


class RaidAttackCardLevel(BaseModel):
    id: model_type.Card
    value: int


class RaidAttackCardDamageLog(BaseModel):
    id: model_type.TitanPart
    value: int


class RaidAttackCardDamage(BaseModel):
    titan_index: int
    id: model_type.Card | None
    damage_log: tuple[RaidAttackCardDamageLog, ...]


class RaidAttackLog(BaseModel):
    cards_damage: tuple[RaidAttackCardDamage, ...]
    cards_level: tuple[RaidAttackCardLevel, ...]
    attack_datetime: datetime


class RaidAttackPlayer(Player):
    raid_level: int
    attacks_remaining: int


class RaidAttack(BaseModel):
    pass
    #clan_code: ClanCode
    #raid_id: int
    #player: RaidAttackPlayer
    #attack_log: RaidAttackLog
    #raid_state: RaidAttackRaidState
