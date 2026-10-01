"""
Bot-wide premium-emoji patch.

Importing this module (done once, from `STRABERRY/__init__.py`, before the
bot client is used) makes *every* outgoing message and caption in the
whole project render its emoji as ZNV CLAN premium/custom emoji -- with
zero changes needed in any of the ~180 plugin/command files.

Why a patch instead of editing every file
------------------------------------------
Pyrogram's high-level helpers -- `Message.reply_text`, `Message.reply`,
`Message.edit_text`, `Message.reply_photo`, `Chat.send_message`, etc. --
all funnel down into a small, fixed set of low-level `Client` methods
(`send_message`, `edit_message_text`, `send_photo`, ...). Patching only
those ~10 `Client` methods therefore covers every command in every
plugin automatically and consistently, whether a file calls
`client.send_message(...)` directly or `message.reply_text(...)` --
there is no call site left uncovered, and no risk of a hand-edit typo
breaking one of ~1400 individual send/reply calls across the codebase.

What gets touched, what doesn't
--------------------------------
- Message text and media captions: converted, always, on every call,
  regardless of which plugin/command sent them.
- Whatever `parse_mode` (or lack of one) the original call already used
  is preserved exactly -- Pyrogram's own parser resolves it the same
  way it always did, so **markdown**, <b>HTML</b>, and plain calls with
  no parse_mode at all keep rendering identically; only the emoji on
  top change.
- Calls that already build their own explicit `entities=` /
  `caption_entities=` list are left completely alone -- we never
  clobber hand-built entities.
- InlineKeyboardButton labels are never touched: Telegram's Bot API has
  no support for custom-emoji entities on buttons, full stop, so button
  emoji stay plain unicode (this is a Telegram limitation, not
  something this patch works around).
- Callback-query alerts (`answer_callback_query`) aren't patched --
  alert popups are plain text only on Telegram's side and can't carry
  entities either.
- If anything about a given call ever goes wrong (encoding oddity,
  unexpected argument shape, etc.) the patch logs it and silently falls
  back to sending the original, unmodified text -- a bug in the emoji
  overlay can never turn into a bot-wide crash or a failed command.
"""

import functools
import logging

from pyrogram import Client

from .premium_emoji import premium

log = logging.getLogger(__name__)

# name -> (kwarg holding the text/caption, its position in *args if passed
# positionally, the kwarg holding pre-built entities for that text)
_METHOD_SPECS = {
    "send_message": ("text", 1, "entities"),
    "edit_message_text": ("text", 2, "entities"),
    "send_photo": ("caption", 2, "caption_entities"),
    "send_video": ("caption", 2, "caption_entities"),
    "send_audio": ("caption", 2, "caption_entities"),
    "send_document": ("caption", 2, "caption_entities"),
    "send_animation": ("caption", 2, "caption_entities"),
    "send_voice": ("caption", 2, "caption_entities"),
    "edit_message_caption": ("caption", 2, "caption_entities"),
}


def _make_wrapper(name, text_key, text_pos, entities_key):
    original = getattr(Client, name)

    @functools.wraps(original)
    async def wrapper(self, *args, **kwargs):
        orig_args, orig_kwargs = args, kwargs
        patched = False

        # Respect any entities the caller already built by hand.
        if kwargs.get(entities_key) is None:
            text_value = kwargs.get(text_key)
            arg_index = None
            if text_value is None and len(args) > text_pos:
                text_value = args[text_pos]
                arg_index = text_pos

            if text_value and isinstance(text_value, str):
                try:
                    new_text, new_entities = await premium(
                        self, text_value, kwargs.get("parse_mode")
                    )
                    if arg_index is not None:
                        args = list(args)
                        args[arg_index] = new_text
                        args = tuple(args)
                    else:
                        kwargs = dict(kwargs)
                        kwargs[text_key] = new_text
                    kwargs = dict(kwargs)
                    kwargs[entities_key] = new_entities
                    # entities and parse_mode are mutually exclusive on
                    # Telegram's side -- the text is already parsed.
                    kwargs.pop("parse_mode", None)
                    patched = True
                except Exception:
                    log.exception(
                        "premium-emoji patch failed for Client.%s(); "
                        "sending original text unmodified",
                        name,
                    )

        try:
            return await original(self, *args, **kwargs)
        except Exception:
            if patched:
                # The emoji overlay itself computed fine, but pyrogram
                # rejected the resulting call (wrong entity shape, peer
                # resolution issue, etc.) -- fall back to the caller's
                # original, unmodified text/entities instead of letting
                # a patch bug take down the whole send (and, if this was
                # a startup message, the bot itself).
                log.exception(
                    "premium-emoji patch produced a send that pyrogram "
                    "rejected for Client.%s(); retrying with original "
                    "unmodified text",
                    name,
                )
                return await original(self, *orig_args, **orig_kwargs)
            raise

    return wrapper


def apply() -> None:
    """Patch every method in `_METHOD_SPECS` onto `pyrogram.Client`.

    Safe to call more than once (e.g. if this module ends up imported
    from two different places) -- a guard flag stops it from wrapping
    an already-wrapped method a second time.
    """
    if getattr(Client, "_premium_emoji_patched", False):
        return

    for name, (text_key, text_pos, entities_key) in _METHOD_SPECS.items():
        setattr(Client, name, _make_wrapper(name, text_key, text_pos, entities_key))

    Client._premium_emoji_patched = True
    log.info(
        "Premium-emoji patch applied to %d Client methods (%s)",
        len(_METHOD_SPECS),
        ", ".join(_METHOD_SPECS),
    )


apply()
