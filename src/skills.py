"""Shared skill logic for human players and bots."""

from src.settings import SKILL_BALANCE, SKILL_FEEDBACK_DURATION

SKILL_DEFINITIONS = SKILL_BALANCE


def set_skill_feedback(actor, skill_name, message=None, position=None, duration=SKILL_FEEDBACK_DURATION):
    """Attach a short-lived visual feedback payload to an actor."""
    if actor is None:
        return

    actor.skill_feedback = {
        'skill': skill_name,
        'message': message or SKILL_DEFINITIONS.get(skill_name, {}).get('label', skill_name),
        'position': position,
        'time': duration,
        'duration': duration,
    }


def create_skill_state():
    """Return mutable cooldown data for a new actor."""
    return {
        name: {
            'cooldown': 0.0,
            'max_cooldown': definition['max_cooldown'],
            'duration': definition['duration'],
            'label': definition['label'],
        }
        for name, definition in SKILL_DEFINITIONS.items()
    }


def tick_actor_effects(actor, dt):
    """Update skill cooldowns and temporary status effects on an actor."""
    for skill in getattr(actor, 'skills', {}).values():
        skill['cooldown'] = max(0.0, skill.get('cooldown', 0.0) - dt)

    freeze_time = max(0.0, getattr(actor, 'freeze_time', getattr(actor, 'freeze_end_time', 0.0)) - dt)
    actor.freeze_time = freeze_time
    actor.freeze_end_time = freeze_time
    actor.is_frozen = freeze_time > 0.0

    blind_time = max(0.0, getattr(actor, 'blind_time', 0.0) - dt)
    actor.blind_time = blind_time
    actor.is_blinded = blind_time > 0.0

    feedback = getattr(actor, 'skill_feedback', None)
    if feedback:
        feedback['time'] = max(0.0, feedback.get('time', 0.0) - dt)
        if feedback['time'] <= 0.0:
            actor.skill_feedback = None


def apply_freeze(actor, duration):
    """Freeze an actor for at least the requested duration."""
    actor.freeze_time = max(getattr(actor, 'freeze_time', 0.0), duration)
    actor.freeze_end_time = actor.freeze_time
    actor.is_frozen = True
    set_skill_feedback(actor, 'freeze', message='FROZEN', duration=min(duration, 1.4))


def apply_blind(actor, duration):
    """Blind an actor for at least the requested duration."""
    actor.blind_time = max(getattr(actor, 'blind_time', 0.0), duration)
    actor.is_blinded = True
    set_skill_feedback(actor, 'blind', message='BLINDED', duration=min(duration, 1.4))


def _target_is_valid(user, target):
    """Return True when a sabotage skill can be applied to the target."""
    if target is None or target is user:
        return False
    return getattr(target, 'health', 0) > 0


def use_actor_skill(user, skill_name, own_map=None, target=None, target_map=None):
    """Activate a skill for any actor that exposes a `skills` dict."""
    skills = getattr(user, 'skills', {})
    if skill_name not in skills:
        return False

    skill = skills[skill_name]
    if skill.get('cooldown', 0.0) > 0.0:
        return False

    definition = SKILL_DEFINITIONS[skill_name]
    result = {'skill': skill_name, 'target': None, 'position': None}

    if definition['requires_target'] and not _target_is_valid(user, target):
        return False

    if skill_name == 'freeze':
        apply_freeze(target, skill['duration'])
        result['target'] = getattr(target, 'player_id', None)
        set_skill_feedback(user, skill_name, message='FREEZE!')
    elif skill_name == 'blind':
        apply_blind(target, skill['duration'])
        result['target'] = getattr(target, 'player_id', None)
        set_skill_feedback(user, skill_name, message='BLIND!')
    elif skill_name == 'extra_hint':
        if own_map is None:
            return False
        position = own_map.reveal_next_objective(user)
        if position is None:
            return False
        result['position'] = position
        set_skill_feedback(user, skill_name, message='EXTRA HINT', position=position)
    else:
        return False

    skill['cooldown'] = skill['max_cooldown']
    user.last_skill_result = result
    return True
