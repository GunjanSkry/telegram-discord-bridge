"""Discord handler."""
import asyncio
import sys
from typing import List

import discord
from discord import MessageReference

from config import Config
from logger import app_logger
from utils import get_discord_message_id, split_message

logger = app_logger()


async def start_discord(config: Config) -> discord.Client:
    """Start the Discord client."""
    async def start_discord_client(discord_client: discord.Client, token: str):
        try:
            logger.info("Starting Discord client...")
            await discord_client.start(token)
            logger.info("Discord client started the session: %s, with identity: %s",
                        config.app_name, discord_client.user.id)
        except (discord.LoginFailure, TypeError) as login_failure:
            logger.error(
                "Error while connecting to Discord: %s", login_failure)
            sys.exit(1)

    discord_client = discord.Client(intents=discord.Intents.default())
    _ = asyncio.ensure_future(
        start_discord_client(discord_client, config.discord.bot_token))

    return discord_client


async def forward_to_discord(discord_channel, message_text: str,
                             image_file=None, reference=None):
    """Send a message to Discord."""
    sent_messages = []
    message_parts = split_message(message_text)
    if image_file:
        discord_file = discord.File(image_file)
        sent_message = await discord_channel.send(message_parts[0],
                                                  file=discord_file,
                                                  reference=reference)
        sent_messages.append(sent_message)
        message_parts.pop(0)

    for part in message_parts:
        sent_message = await discord_channel.send(part, reference=reference)
        sent_messages.append(sent_message)

    return sent_messages


async def fetch_discord_reference(event, discord_channel):
    """Fetch the Discord message reference."""
    discord_message_id = get_discord_message_id(
        event.message.reply_to_msg_id)
    if not discord_message_id:
        logger.debug("No mapping found for TG message %s",
                     event.message.reply_to_msg_id)
        return None

    try:
        messages = []
        async for message in discord_channel.history(around=discord.Object(id=discord_message_id),   # pylint: disable=line-too-long
                                                     limit=10):
            messages.append(message)

        discord_message = next(
            (msg for msg in messages if msg.id == discord_message_id), None)
        if not discord_message:
            logger.debug(
                "Reference Discord message not found for TG message %s",
                event.message.reply_to_msg_id)
            return None

        return MessageReference.from_message(discord_message)
    except discord.NotFound:
        logger.debug("Reference Discord message not found for TG message %s",
                     event.message.reply_to_msg_id)
        return None


def get_mention_roles(message_forward_hashtags: List[str],
                      mention_override: dict,
                      discord_built_in_roles: List[str],
                      server_roles: List[discord.Role]) -> List[str]:
    """Get the roles to mention."""
    mention_roles = set()

    for tag in message_forward_hashtags:
        if tag.lower() in mention_override:
            logger.debug("Found mention override for tag %s: %s",
                         tag, mention_override[tag.lower()])
            for role_name in mention_override[tag.lower()]:
                if is_builtin_mention(role_name, discord_built_in_roles):
                    mention_roles.add("@" + role_name)
                else:
                    role = discord.utils.get(server_roles, name=role_name)
                    if role:
                        mention_roles.add(role.mention)

    return list(mention_roles)


def is_builtin_mention(role_name: str, discord_built_in_roles: List[str]) -> bool:
    """Check if a role name is a Discord built-in mention."""
    return role_name.lower() in discord_built_in_roles
