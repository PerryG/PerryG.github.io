"""Bot client for Res Arcana - acts as an AI player."""

import requests
import time
import random
import argparse


class BotClient:
    """A bot that plays Res Arcana by polling the server and taking actions."""

    def __init__(self, base_url: str, player_id: int):
        self.base_url = base_url.rstrip('/')
        self.player_id = player_id
        self.last_state = None

    def get_state(self) -> dict:
        """Fetch current game state from server (filtered to this player's view)."""
        resp = requests.get(f'{self.base_url}/api/state', params={'playerId': self.player_id})
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint: str, data: dict) -> dict:
        """POST to an API endpoint."""
        resp = requests.post(f'{self.base_url}{endpoint}', json=data)
        resp.raise_for_status()
        return resp.json()

    def run(self):
        """Main loop - poll and act."""
        print(f"Bot player {self.player_id} starting...")

        while True:
            try:
                state = self.get_state()
                if state is None:
                    print("No game in progress, waiting...")
                    time.sleep(1)
                    continue

                self.last_state = state
                action_taken = self.take_action(state)

                if action_taken:
                    print(f"  Action taken in phase: {state['phase']}")

            except requests.exceptions.ConnectionError:
                print("Server not available, retrying...")
            except Exception as e:
                print(f"Error: {e}")

            time.sleep(0.5)

    def take_action(self, state: dict) -> bool:
        """Take an action based on current game phase. Returns True if action taken."""
        phase = state['phase']

        if phase == 'drafting_round_1' or phase == 'drafting_round_2':
            return self.handle_draft(state)
        elif phase == 'mage_selection':
            return self.handle_mage_selection(state)
        elif phase == 'magic_item_selection':
            return self.handle_magic_item_selection(state)
        elif phase == 'income':
            return self.handle_income(state)
        elif phase == 'playing':
            # No actions yet - will expand later
            return False

        return False

    def handle_draft(self, state: dict) -> bool:
        """Pick a random card during drafting."""
        draft_state = state.get('draftState')
        if not draft_state:
            return False

        cards_to_pick = draft_state['cardsToPick'].get(str(self.player_id), [])
        if not cards_to_pick:
            return False

        # Check if we've already picked (no cards means waiting for pass)
        drafted = draft_state['draftedCards'].get(str(self.player_id), [])
        # In each round we pick 4 cards, one at a time
        # If cards_to_pick is empty or we can't pick, skip

        # Pick a random card
        card = random.choice(cards_to_pick)
        print(f"Bot {self.player_id} picking card: {card['name']}")

        self.post('/api/draft/pick', {
            'playerId': self.player_id,
            'cardName': card['name']
        })
        return True

    def handle_mage_selection(self, state: dict) -> bool:
        """Pick a random mage."""
        draft_state = state.get('draftState')
        if not draft_state:
            return False

        # Check if already selected
        selected = draft_state['selectedMage'].get(str(self.player_id))
        if selected is not None:
            return False

        mage_options = draft_state['mageOptions'].get(str(self.player_id), [])
        if not mage_options:
            return False

        mage = random.choice(mage_options)
        print(f"Bot {self.player_id} selecting mage: {mage['name']}")

        self.post('/api/mage/select', {
            'playerId': self.player_id,
            'mageName': mage['name']
        })
        return True

    def handle_magic_item_selection(self, state: dict) -> bool:
        """Pick a magic item when it's our turn."""
        draft_state = state.get('draftState')
        if not draft_state:
            return False

        # Check if it's our turn
        selector = draft_state.get('magicItemSelector')
        if selector != self.player_id:
            return False

        available = state.get('availableMagicItems', [])
        if not available:
            return False

        item = random.choice(available)
        print(f"Bot {self.player_id} taking magic item: {item['name']}")

        self.post('/api/magic-item/select', {
            'playerId': self.player_id,
            'itemName': item['name']
        })
        return True

    def handle_income(self, state: dict) -> bool:
        """Handle income phase - make choices and finalize."""
        income_state = state.get('incomeState')
        if not income_state:
            return False

        pid_str = str(self.player_id)

        # Check if already finalized
        if income_state['finalized'].get(pid_str, False):
            return False

        # Make income choices for cards that need them
        cards_info = income_state.get('cardsInfo', {}).get(pid_str, {})

        # Handle cards needing income choice
        cards_needing_choice = cards_info.get('cardsNeedingChoice', [])
        current_choices = income_state.get('incomeChoices', {}).get(pid_str, {})

        for card_info in cards_needing_choice:
            card_name = card_info['cardName']
            if card_name not in current_choices:
                # Make a random choice
                count = card_info['count']
                types = card_info['types']

                # Distribute resources randomly among available types
                resources = {}
                for _ in range(count):
                    chosen_type = random.choice(types)
                    resources[chosen_type] = resources.get(chosen_type, 0) + 1

                print(f"Bot {self.player_id} choosing income for {card_name}: {resources}")
                self.post('/api/income/income-choice', {
                    'playerId': self.player_id,
                    'cardName': card_name,
                    'resources': resources
                })
                return True

        # Handle collection choices - randomly decide to take or leave
        cards_with_resources = cards_info.get('cardsWithResources', [])
        current_collection = income_state.get('collectionChoices', {}).get(pid_str, {})

        for card_info in cards_with_resources:
            card_name = card_info['cardName']
            if card_name not in current_collection:
                take_all = random.choice([True, False])
                print(f"Bot {self.player_id} {'taking' if take_all else 'leaving'} resources from {card_name}")
                self.post('/api/income/collection-choice', {
                    'playerId': self.player_id,
                    'cardName': card_name,
                    'takeAll': take_all
                })
                return True

        # All choices made, finalize
        print(f"Bot {self.player_id} finalizing income")
        self.post('/api/income/finalize', {
            'playerId': self.player_id
        })
        return True


def main():
    parser = argparse.ArgumentParser(description='Res Arcana Bot Client')
    parser.add_argument('player_id', type=int, help='Player ID for this bot (0-indexed)')
    parser.add_argument('--url', default='http://localhost:5001', help='Server URL')

    args = parser.parse_args()

    bot = BotClient(args.url, args.player_id)
    bot.run()


if __name__ == '__main__':
    main()
