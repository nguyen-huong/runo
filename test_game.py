import os
import unittest
from uno import *

TEST_GAME_FILE_PATH = 'games_test'

class GameTestCase(unittest.TestCase):
    def setUp(self):
        set_GAME_FILE_PATH(TEST_GAME_FILE_PATH)

    def tearDown(self):
        old_dir = os.getcwd()
        os.chdir(old_dir + '/' + TEST_GAME_FILE_PATH)
        for game_file in os.listdir('.'):
            os.remove(game_file)
        os.chdir(old_dir)

    def test_create_new_game(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertIsNotNone(game_data)

    def test_save_state(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        result = save_state(game_data)
        self.assertTrue(result)

    def test_load_state(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data = load_state(game_data['id'])
        self.assertNotEqual(game_data, {})

    def test_new_game_deck_has_108_cards(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertEqual(len(game_data['deck']), 108)

    def test_new_game_is_not_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertFalse(game_data['active'])

    def test_new_game_is_not_reversed(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertFalse(game_data['reverse'])

    def test_new_game_created_at(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertIsNotNone(game_data['created_at'])

    def test_started_at_is_none_before_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertIsNone(game_data['started_at'])

    def test_started_at_is_not_none_after_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        self.assertIsNotNone(game_data['started_at'])

    def test_stack_has_no_cards_before_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertEqual(len(game_data['stack']), 0)

    def test_stack_has_one_card_after_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        self.assertEqual(len(game_data['stack']), 1)

    def test_player_that_creates_game_is_admin_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertTrue(game_data['players'][0]['admin'])

    def test_add_player_to_game(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        player = add_player_to_game(game_data, 'PlayerTwo')
        self.assertIsNotNone(player)
        self.assertEqual(len(game_data['players']), 2)

    def test_each_player_has_seven_cards_after_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        for player in game_data['players']:
            self.assertEqual(len(player['hand']), 7)

    def test_no_player_is_active_before_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        for player in game_data['players']:
            self.assertFalse(player['active'])

    def test_admin_player_is_active_after_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        admin_player = [p for p in game_data['players'] if p['admin']][0]
        self.assertTrue(admin_player['active'])

    def test_get_state(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_id = game_data['id']
        player_id = game_data['players'][0]['id']
        result = get_state(game_id, player_id)
        self.assertEqual(result, game_data)

    def test_get_state_returns_empty_when_game_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        player_id = game_data['players'][0]['id']
        result = get_state('bad_game_id', player_id)
        self.assertEqual(result, {})

    def test_get_state_returns_empty_when_player_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_id = game_data['id']
        result = get_state(game_id, 'bad_player_id')
        self.assertEqual(result, {})

    def test_get_state_masks_id_of_other_players(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        game_id = game_data['id']
        player_one_id = game_data['players'][0]['id']
        result = get_state(game_id, player_one_id)
        self.assertEqual(result['players'][0]['id'], player_one_id)
        self.assertIsNone(result['players'][1]['id'])

    def test_get_state_masks_hand_of_other_players(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        game_id = game_data['id']
        player_one_id = game_data['players'][0]['id']
        result = get_state(game_id, player_one_id)
        for card in result['players'][0]['hand']:
            self.assertIn(card, game_data['players'][0]['hand'])
        for card in result['players'][1]['hand']:
            self.assertNotIn(card, game_data['players'][1]['hand'])

    def test_get_active_player_returns_none_before_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        result = get_active_player(game_data)
        self.assertIsNone(result)

    def test_get_active_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_fails_before_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        with self.assertRaises(ValueError):
            activate_next_player(game_data)

    def test_activate_next_player_succeeds_even_if_only_one_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        current_player = get_active_player(game_data)
        activate_next_player(game_data)
        next_player = get_active_player(game_data)
        self.assertEqual(current_player, next_player)

    def test_activate_next_player_cycle_two_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Ensure top of stack isn't a REVERSE or SKIP card
        game_data['stack'][-1]['value'] = 0
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_cycle_two_player_reverse(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data['reverse'] = True
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Ensure top of stack isn't a REVERSE or SKIP card
        game_data['stack'][-1]['value'] = 0
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_cycle_multi_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        # Ensure top of stack isn't a SKIP card
        game_data['stack'][-1]['value'] = 0
        for i in range(0, 4):
            active_player = get_active_player(game_data)
            self.assertEqual(active_player, game_data['players'][i])
            activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_cycle_multi_player_reverse(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data['reverse'] = True
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        # Ensure top of stack isn't a SKIP card
        game_data['stack'][-1]['value'] = 0
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        for i in range(3, -1, -1):
            activate_next_player(game_data)
            active_player = get_active_player(game_data)
            self.assertEqual(active_player, game_data['players'][i])

    def test_activate_next_player_with_reverse_card_two_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set the top of stack to a REVERSE card
        game_data['stack'][-1]['value'] = 'REVERSE'
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_with_skip_card_two_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set the top of stack to a SKIP card
        game_data['stack'][-1]['value'] = 'SKIP'
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_with_skip_card_two_player_reverse(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data['reverse'] = True
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set the top of stack to a SKIP card
        game_data['stack'][-1]['value'] = 'SKIP'
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_with_skip_card_multi_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        # Set the top of stack to a SKIP card
        game_data['stack'][-1]['value'] = 'SKIP'
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][2])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_with_skip_card_multi_player_reverse(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data['reverse'] = True
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        # Set the top of stack to a SKIP card
        game_data['stack'][-1]['value'] = 'SKIP'
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][2])
        activate_next_player(game_data)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_can_play_card_succeeds_with_any_special_card(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set the top of stack to an arbitrary card color and value
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = 5
        card = create_card('WILD')
        self.assertTrue(can_play_card(game_data, card))
        card = create_card('WILD_DRAW_FOUR')
        self.assertTrue(can_play_card(game_data, card))

    def test_can_play_card_succeeds_with_matching_color(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        card_values = CARD_VALUES + SPECIAL_COLOR_CARDS
        game_data['stack'][-1] = create_card('any_value', 'RED')
        for value in CARD_VALUES:
            card = create_card(value, 'RED')
            self.assertTrue(can_play_card(game_data, card))

    def test_can_play_card_succeeds_with_matching_value(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['stack'][-1] = create_card('5', 'any_color')
        for color in CARD_COLORS:
            card = create_card('5', color)
            self.assertTrue(can_play_card(game_data, card))

    def test_can_play_card_fails_if_color_and_value_not_matching(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set the top of stack to an arbitrary card color and value
        game_data['stack'][-1] = create_card('5', 'GREEN')
        # Pick a card that doesn't have a matching value or color
        card = create_card('6', 'RED')
        self.assertFalse(can_play_card(game_data, card))

    def test_reclaim_stack(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['deck'] = []
        game_data['stack'] = ['card', 'card', 'card', 'top']
        reclaim_stack(game_data)
        self.assertEqual(game_data['stack'], ['top'])
        self.assertEqual(game_data['deck'], ['card', 'card', 'card'])

    def test_draw_card(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        draw_card(game_data, player)
        self.assertEqual(len(player['hand']), 8)

    def test_draw_cards_triggers_reclaim_stack(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['deck'] = ['card', 'card', 'card']
        game_data['stack'] = ['card', 'card', 'card', 'top']
        player = game_data['players'][0]
        draw_card(game_data, player)
        draw_card(game_data, player)
        draw_card(game_data, player)
        self.assertEqual(len(player['hand']), 10)
        self.assertEqual(game_data['stack'], ['top'])
        self.assertEqual(game_data['deck'], ['card', 'card', 'card'])

    def test_draw_two(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['deck'] = ['card', 'card']
        game_data['stack'] = ['card', 'card', 'card', 'top']
        player = game_data['players'][0]
        draw_two(game_data, player)
        self.assertEqual(len(player['hand']), 9)
        self.assertEqual(game_data['stack'], ['top'])
        self.assertEqual(game_data['deck'], ['card', 'card', 'card'])

    def test_draw_four(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['deck'] = ['card', 'card', 'card', 'card']
        game_data['stack'] = ['card', 'card', 'card', 'top']
        player = game_data['players'][0]
        draw_four(game_data, player)
        self.assertEqual(len(player['hand']), 11)
        self.assertEqual(game_data['stack'], ['top'])
        self.assertEqual(game_data['deck'], ['card', 'card', 'card'])


if __name__ == '__main__':
    tests = unittest.TestLoader().loadTestsFromTestCase(GameTestCase)
    unittest.TextTestRunner(verbosity=2).run(tests)
