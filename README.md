# thegate_discordbot
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)

An outline for a faction, economy and events **interserver** bot in **Python**.
### You can use this model freely to create an amazing bot (with some knowledge of the discord library and python).

---

## Overview

The Gate bot is outline for a faction, economy and events **interserver** bot in **Python** with a bunch of features, but some of them are not finished or are not optimal in terms of code and use.
Note that it's an old project that I started for my discord server and that I won't be continuing, but I know that the bot has a lot of potential and original mechanisms/commands that could be very appealing. I'm convinced that if you're planning to create or add functionality to your discord bot, this repository can provide you with some interesting resources.
The project does not fully comply with PEP-8 btw.

---

## Features
### Global :
1. Command Prefix and Intents:
- Command prefix is set to '!' and you can change it.

2. Blacklist and Owner:
- You can put user IDs into a blacklist system.
- You can custom Owner ID.

3. Voice Rewards:
- You can gain rewards based on different voice states and corresponding reward values (here its coins to link the voice rewards system with the economy system of the bot).

4. Report mechanic:
- report command for users to report others users.

5. Cooldown Management:
- Cooldowns are implemented for certain commands to prevent abuse.

6. Logging:
- Basic logging is configured.
- register command: Registers a user.

### 7. Event System:
- Event-related dictionaries (events and reputation).
- create_event : command to create events.
- update_event_status : function to update event statuses.
- list_events command : to display current events.
- delete_event command : to delete events.
- join command : for users to join events.
- rep : command to check server reputation (reputation system based).

 8. Factions System:

- save_factions(factions): Saves the factions to a JSON file.
- load_factions(): Loads the factions from the JSON file.

#### - Faction Commands:
- createfaction(ctx, faction_name): Creates a new faction.
- joinfaction(ctx, faction_name): Allows a user to join an existing faction.
- leavefaction(ctx): Allows a user to leave their current faction.
- factioninfo(ctx, faction_name): Displays information about a specific faction.
- factionleaderboard(ctx): Displays a leaderboard of factions based on the number of members.
- factioninvite(ctx, user): Allows a faction leader to invite a user to join their faction.
- acceptinvite(ctx, faction_name): Allows a user to accept a faction invitation.
- factionkick(ctx, user): Allows a faction leader to kick a member from their faction.
- factionmessage(ctx, message): Sends a message to all members of the user's faction.
- factionrename(ctx, new_name): Allows a faction leader to rename their faction.
- factionwar(ctx, target_faction): Initiates a war between two factions (placeholder functionality).
- factionquest(ctx): Launches a quest for the user's faction (placeholder functionality).
- factiontrade(ctx, target_faction, offer): Initiates a trade between two factions (placeholder functionality).
- factionalliance(ctx, target_faction): Proposes an alliance between two factions (placeholder functionality).
- factionranking(ctx, sort_by='members'): Displays a faction leaderboard sorted by a specified parameter.
- factionpromote(ctx, member): Allows a faction leader to promote a member to a commander.
- factiondemote(ctx, member): Allows a faction leader to demote a commander to a member.
- factiondisband(ctx): Allows a faction leader to disband their faction.
- factiontransfer(ctx, new_leader): Allows a faction leader to transfer leadership to another member.
- factionmembers(ctx): Displays a list of members in the user's faction.

#### - Helper Function:
- get_user_faction(user_id, factions): Retrieves the faction to which a user belongs.

Some commands have placeholder functionality marked with comments such as # todo: complete "function_name" function. You'll need to implement the specific logic for those commands based on your bot's requirements.

### 9. Economy System:
#### - Economy Data Handling:
- economie_data(): Writes the economy data to a file (eco_data.txt).
- read_economie_data(): Reads the economy data from the file (eco_data.txt).
- check_user(): Checks if a user is registered and not blacklisted.

#### - Voice State Integration:
- get_voice_state(member): Determines the voice state of a member based on streaming, video, deafened, and muted states.
- update_balance(): Updates user balances based on mining and wagon activities.
- voice_rewards(): Rewards users based on their voice activity.

#### - Economy Commands:
- balance: Retrieves the balance of a registered user.
- give: Transfers coins from one user to another.
- daily: Grants a daily coin reward to the user.
- shop: Displays available items in the shop.
- buy: Allows users to buy items from the shop.
- withdraw and !deposit: Manages the withdrawal and deposit of coins.
- casino: Provides various casino games like guessing, high-low, slots, emoji match, memory, treasure hunt, and odd or even.

#### - Games Implementation:
- play_highlow_game: High-low guessing game with a chance to win coins.
- play_guessing_game: Number guessing game with three attempts.
- slots: Slot machine game with potential coin rewards.
- play_emoji_match: Emoji matching game with randomized rewards.
- play_treasure_hunt: Treasure hunt game with chests and potential rewards.
- play_odd_or_even: Odd or even guessing game with coin rewards.
- play_memory_game: Memory game with emojis for players to recall.
---

## Usage

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/GentlemanAxel/thegate_discordbot.git
    ```

2. Navigate to the project directory:

    ```bash
    cd thegate_discordbot
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Run the Application

```bash
python thegate.py
```

---

### Credits

<a href='https://github.com/GentlemanAxel' target="_blank"><img alt='GitHub' src='https://img.shields.io/badge/GentlemanAxel-100000?style=for-the-badge&logo=GitHub&logoColor=white&labelColor=black&color=CA2C2C'/></a>

