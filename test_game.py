import os
import unittest
from runo import *

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

    def test_create_new_game_low_min_players(self):
        game_data = create_new_game('MyGame', 'PlayerOne', min_players=1)
        self.assertEqual(game_data['min_players'], 2)

    def test_create_new_game_high_max_players(self):
        game_data = create_new_game('MyGame', 'PlayerOne', max_players=11)
        self.assertEqual(game_data['max_players'], 10)

    def test_create_new_game_defaults(self):
        game_data = create_new_game('', '', points_to_win='', min_players='',
                                    max_players='')
        self.assertEqual(game_data['name'], DEFAULT_GAME_NAME)
        self.assertEqual(game_data['players'][0]['name'], DEFAULT_PLAYER_NAME)
        self.assertEqual(game_data['points_to_win'],
                         POINTS_TO_WIN)
        self.assertEqual(game_data['min_players'],
                         MIN_PLAYERS)
        self.assertEqual(game_data['max_players'],
                         MAX_PLAYERS)
        game_data = create_new_game(None, None, points_to_win=None,
                                    min_players=None, max_players=None)
        self.assertEqual(game_data['name'], DEFAULT_GAME_NAME)
        self.assertEqual(game_data['players'][0]['name'], DEFAULT_PLAYER_NAME)
        self.assertEqual(game_data['points_to_win'],
                         POINTS_TO_WIN)
        self.assertEqual(game_data['min_players'],
                         MIN_PLAYERS)
        self.assertEqual(game_data['max_players'],
                         MAX_PLAYERS)

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

    def test_add_player_to_game_fails_when_max_players_reached(self):
        game_data = create_new_game('MyGame', 'PlayerOne', max_players=2)
        player2 = add_player_to_game(game_data, 'PlayerTwo')
        self.assertIsNotNone(player2)
        player3 = add_player_to_game(game_data, 'PlayerThree')
        self.assertIsNone(player3)
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
        save_state(game_data)
        game_id = game_data['id']
        player_one_id = game_data['players'][0]['id']
        result = get_state(game_id, player_one_id)
        self.assertEqual(result['players'][0]['id'], player_one_id)
        self.assertIsNone(result['players'][1]['id'])

    def test_get_state_masks_hand_of_other_players(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        save_state(game_data)
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
        with self.assertRaises(TypeError):
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

    def test_activate_next_player_draw_two_card_two_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Add a DRAW_TWO card to the stack
        game_data['stack'].append(create_card('DRAW_TWO', 'GREEN'))
        activate_next_player(game_data)
        affected_player = game_data['players'][1]
        self.assertEqual(len(affected_player['hand']), 9)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_draw_two_card_multi_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        # Add a DRAW_TWO card to the stack
        game_data['stack'].append(create_card('DRAW_TWO', 'GREEN'))
        activate_next_player(game_data)
        affected_player = game_data['players'][1]
        self.assertEqual(len(affected_player['hand']), 9)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][2])

    def test_activate_next_player_draw_four_card_two_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Add a WILD_DRAW_FOUR card to the stack
        game_data['stack'].append(create_card('WILD_DRAW_FOUR'))
        activate_next_player(game_data)
        affected_player = game_data['players'][1]
        self.assertEqual(len(affected_player['hand']), 11)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][0])

    def test_activate_next_player_draw_four_card_multi_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        # Add a WILD_DRAW_FOUR card to the stack
        game_data['stack'].append(create_card('WILD_DRAW_FOUR'))
        activate_next_player(game_data)
        affected_player = game_data['players'][1]
        self.assertEqual(len(affected_player['hand']), 11)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][2])

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

    def test_draw_two_triggers_reclaim_stack(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['deck'] = ['card', 'card']
        game_data['stack'] = ['card', 'card', 'card', 'top']
        player = game_data['players'][0]
        draw_two(game_data, player)
        self.assertEqual(len(player['hand']), 9)
        self.assertEqual(game_data['stack'], ['top'])
        self.assertEqual(game_data['deck'], ['card', 'card', 'card'])

    def test_draw_four_triggers_reclaim_stack(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        game_data['deck'] = ['card', 'card', 'card', 'card']
        game_data['stack'] = ['card', 'card', 'card', 'top']
        player = game_data['players'][0]
        draw_four(game_data, player)
        self.assertEqual(len(player['hand']), 11)
        self.assertEqual(game_data['stack'], ['top'])
        self.assertEqual(game_data['deck'], ['card', 'card', 'card'])

    def test_deal_cards_avoid_starting_stack_with_special_cards(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        for special_type in SPECIAL_CARDS + SPECIAL_COLOR_CARDS:
            game_data['deck'] = []
            for __ in range(8):
                game_data['deck'].append(create_card(special_type, 'any_color'))
            start_game(game_data)
            self.assertFalse(game_data['stack'])

    def test_play_card(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        # The card played should be on top of the stack
        self.assertEqual(game_data['stack'][-1], card)
        # Stack should contain two cards now
        self.assertEqual(len(game_data['stack']), 2)
        # Player's hand should contain one less than the original seven
        self.assertEqual(len(player['hand']), 6)
        # The second player should now be the active player
        self.assertEqual(get_active_player(game_data), game_data['players'][1])

    def test_play_card_fails_when_game_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        save_state(game_data)
        result = play_card('bad_game_id', player['id'], card['id'])
        self.assertFalse(result)

    def test_play_card_fails_when_player_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        save_state(game_data)
        result = play_card(game_data['id'], 'bad_player_id', card['id'])
        self.assertFalse(result)

    def test_play_card_fails_when_card_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], 'bad_card_id')
        self.assertFalse(result)

    def test_play_card_fails_when_player_not_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        player['active'] = False
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'])
        self.assertFalse(result)

    def test_play_card_fails_when_game_not_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        game_data['active'] = False
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'])
        self.assertFalse(result)

    def test_play_card_fails_if_card_not_playable(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = '5'
        card['color'] = 'RED'
        game_data['stack'][-1]['value'] = '4'
        game_data['stack'][-1]['color'] = 'GREEN'
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'])
        self.assertFalse(result)

    def test_play_card_fails_if_special_card_with_no_selected_color(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = 'WILD'
        card['color'] = None
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'])
        self.assertFalse(result)
        player = game_data['players'][1]
        card = player['hand'][0]
        card['value'] = 'WILD_DRAW_FOUR'
        card['color'] = None
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'])
        self.assertFalse(result)

    def test_play_card_fails_if_special_card_with_bad_selected_color(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = 'WILD'
        card['color'] = None
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'], 'PINK')
        self.assertFalse(result)

    def test_play_card_special_card_with_valid_selected_color(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = 'WILD'
        card['color'] = None
        save_state(game_data)
        result = play_card(game_data['id'], player['id'], card['id'], 'RED')
        self.assertTrue(result)

    def test_play_card_sets_reverse_flag_when_reverse_card_is_played(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        card = player['hand'][0]
        card['value'] = 'REVERSE'
        card['color'] = 'RED'
        game_data['stack'][-1]['color'] = 'RED'
        save_state(game_data)
        play_card(game_data['id'], player['id'], card['id'])
        game_data = load_state(game_data['id'])
        self.assertTrue(game_data['reverse'])

    def test_play_card_player_goes_out(self):
        game_data = create_new_game('MyGame', 'PlayerOne', 1)
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        add_player_to_game(game_data, 'PlayerFive')
        start_game(game_data)
        player = game_data['players'][0]
        card = create_card('5', 'GREEN')
        player['hand'] = [card]
        game_data['stack'][-1]['color'] = 'GREEN'
        save_state(game_data)
        play_card(game_data['id'], player['id'], card['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(player['game_winner'])

    def test_play_card_player_goes_out_check_active_player_next_round(self):
        game_data = create_new_game('MyGame', 'PlayerOne', points_to_win=10000)
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        add_player_to_game(game_data, 'PlayerFive')
        start_game(game_data)
        player = game_data['players'][0]
        card = create_card('5', 'GREEN')
        player['hand'] = [card]
        game_data['stack'][-1]['color'] = 'GREEN'
        save_state(game_data)
        play_card(game_data['id'], player['id'], card['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertFalse(player['game_winner'])
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])

    def test_play_card_fails_when_illegal_wild_draw_for_is_played(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to red card
        game_data['stack'][-1]['color'] = 'RED'
        # Ensure the player has a red card
        player = game_data['players'][0]
        player['hand'][0]['value'] = '5'
        player['hand'][0]['color'] = 'RED'
        # Give the player a WILD_DRAW_FOUR card
        player['hand'][1]['value'] = 'WILD_DRAW_FOUR'
        player['hand'][1]['color'] = None
        save_state(game_data)
        card = player['hand'][1]
        result = play_card(game_data['id'], player['id'], card['id'],
                           selected_color='GREEN')
        # Should fail since the WILD_DRAW_FOUR should be allowed if the
        # player has a matching color card that could be played.
        self.assertFalse(result)

    def test_count_points_for_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        player = game_data['players'][0]
        hand = []
        hand.append(create_card('WILD'))
        hand.append(create_card('WILD_DRAW_FOUR'))
        hand.append(create_card('5', 'GREEN'))
        hand.append(create_card('3', 'RED'))
        hand.append(create_card('2', 'BLUE'))
        hand.append(create_card('REVERSE', 'RED'))
        hand.append(create_card('SKIP', 'YELLOW'))
        player['hand'] = hand
        points = count_points_for_player(player)
        self.assertEqual(points, 150)

    def test_count_points(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        hand = []
        hand.append(create_card('WILD'))
        hand.append(create_card('WILD_DRAW_FOUR'))
        hand.append(create_card('5', 'GREEN'))
        hand.append(create_card('3', 'RED'))
        hand.append(create_card('2', 'BLUE'))
        hand.append(create_card('REVERSE', 'RED'))
        hand.append(create_card('SKIP', 'YELLOW'))
        game_data['players'][1]['hand'] = hand
        game_data['players'][2]['hand'] = hand
        winner = game_data['players'][0]
        points = count_points(game_data, winner)
        self.assertEqual(points, 300)

    def test_set_round_winner(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        hand = []
        hand.append(create_card('5', 'GREEN'))
        hand.append(create_card('3', 'RED'))
        hand.append(create_card('2', 'BLUE'))
        hand.append(create_card('REVERSE', 'RED'))
        hand.append(create_card('SKIP', 'YELLOW'))
        game_data['players'][1]['hand'] = hand
        game_data['players'][2]['hand'] = hand
        game_data['players'][3]['hand'] = hand
        winner = game_data['players'][0]
        set_round_winner(game_data, winner)
        self.assertEqual(winner['points'], 150)
        self.assertEqual(winner['rounds_won'], 1)
        self.assertFalse(winner['game_winner'])

    def test_set_round_winner_deal_cards(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        hand = []
        hand.append(create_card('5', 'GREEN'))
        hand.append(create_card('3', 'RED'))
        hand.append(create_card('2', 'BLUE'))
        hand.append(create_card('REVERSE', 'RED'))
        hand.append(create_card('SKIP', 'YELLOW'))
        game_data['players'][1]['hand'] = hand
        game_data['players'][2]['hand'] = hand
        game_data['players'][3]['hand'] = hand
        winner = game_data['players'][0]
        set_round_winner(game_data, winner)
        for player in game_data['players']:
            self.assertEqual(len(player['hand']), 7)

    def test_set_round_winner_triggers_set_game_winner(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        hand = []
        hand.append(create_card('WILD'))
        hand.append(create_card('WILD_DRAW_FOUR'))
        hand.append(create_card('5', 'GREEN'))
        hand.append(create_card('3', 'RED'))
        hand.append(create_card('2', 'BLUE'))
        hand.append(create_card('REVERSE', 'RED'))
        hand.append(create_card('SKIP', 'YELLOW'))
        game_data['players'][1]['hand'] = hand
        game_data['players'][2]['hand'] = hand
        game_data['players'][3]['hand'] = hand
        winner = game_data['players'][0]
        set_round_winner(game_data, winner)
        self.assertTrue(winner['game_winner'])

    def test_set_round_winner_without_set_game_winner_due_to_high_goal(self):
        game_data = create_new_game('MyGame', 'PlayerOne', points_to_win=451)
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        hand = []
        hand.append(create_card('WILD'))
        hand.append(create_card('WILD_DRAW_FOUR'))
        hand.append(create_card('5', 'GREEN'))
        hand.append(create_card('3', 'RED'))
        hand.append(create_card('2', 'BLUE'))
        hand.append(create_card('REVERSE', 'RED'))
        hand.append(create_card('SKIP', 'YELLOW'))
        game_data['players'][1]['hand'] = hand
        game_data['players'][2]['hand'] = hand
        game_data['players'][3]['hand'] = hand
        winner = game_data['players'][0]
        set_round_winner(game_data, winner)
        self.assertFalse(winner['game_winner'])

    def test_game_no_longer_active_after_set_game_winner(self):
        game_data = create_new_game('MyGame', 'PlayerOne', 451)
        start_game(game_data)
        set_game_winner(game_data, game_data['players'][0])
        self.assertFalse(game_data['active'])

    def test_ended_at_not_none_after_set_game_winner(self):
        game_data = create_new_game('MyGame', 'PlayerOne', 451)
        start_game(game_data)
        set_game_winner(game_data, game_data['players'][0])
        self.assertIsNotNone(game_data['ended_at'])

    def test_reclaim_player_cards(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        add_player_to_game(game_data, 'PlayerThree')
        add_player_to_game(game_data, 'PlayerFour')
        start_game(game_data)
        self.assertEqual(len(game_data['deck']), 79)
        top_card = game_data['stack'][-1]
        reclaim_player_cards(game_data)
        self.assertEqual(len(game_data['stack']), 29)
        self.assertEqual(top_card, game_data['stack'][-1])
        for player in game_data['players']:
            self.assertFalse(player['hand'])

    def test_player_draw_card(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)

    def test_player_draw_card_fails_when_game_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        result = player_draw_card('bad_game_id', player['id'])
        self.assertFalse(result)

    def test_player_draw_card_fails_when_player_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        result = player_draw_card(game_data['id'], 'bad_player_id')
        self.assertFalse(result)

    def test_player_draw_card_fails_when_game_not_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        game_data['active'] = False
        player = game_data['players'][0]
        save_state(game_data)
        result = player_draw_card(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_player_draw_card_fails_when_player_not_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        player['active'] = False
        save_state(game_data)
        result = player_draw_card(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_player_draw_card_advances_to_next_player(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set top of deck to a non-matching card, to ensure that the next
        # player is activated after the draw
        game_data['deck'][-1]['color'] = 'BLUE'
        game_data['deck'][-1]['value'] = '7'
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        player = game_data['players'][0]
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])

    def test_player_draw_card_advances_to_next_player_ignore_reverse(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to non-color-matching REVERSE
        game_data['stack'][-1]['value'] = 'REVERSE'
        game_data['stack'][-1]['color'] = 'RED'
        player = game_data['players'][0]
        # Set top of deck to a non-matching card, to ensure that the next
        # player is activated after the draw
        game_data['deck'][-1]['color'] = 'BLUE'
        game_data['deck'][-1]['value'] = '7'
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        player = game_data['players'][0]
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])

    def test_player_draw_card_advances_to_next_player_ignore_skip(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to non-color-matching SKIP
        game_data['stack'][-1]['value'] = 'SKIP'
        game_data['stack'][-1]['color'] = 'RED'
        player = game_data['players'][0]
        # Set top of deck to a non-matching card, to ensure that the next
        # player is activated after the draw
        game_data['deck'][-1]['color'] = 'BLUE'
        game_data['deck'][-1]['value'] = '7'
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        player = game_data['players'][0]
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])

    def test_player_draw_card_advances_to_next_player_ignore_draw_two(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to non-color-matching DRAW_TWO
        game_data['stack'][-1]['value'] = 'DRAW_TWO'
        game_data['stack'][-1]['color'] = 'RED'
        player = game_data['players'][0]
        # Set top of deck to a non-matching card, to ensure that the next
        # player is activated after the draw
        game_data['deck'][-1]['color'] = 'BLUE'
        game_data['deck'][-1]['value'] = '7'
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        player = game_data['players'][0]
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])

    def test_player_draw_card_advances_to_next_player_ignore_draw_four(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to non-color-matching WILD_DRAW_FOUR
        game_data['stack'][-1]['value'] = 'WILD_DRAW_FOUR'
        game_data['stack'][-1]['color'] = 'RED'
        player = game_data['players'][0]
        # Set top of deck to a non-matching card, to ensure that the next
        # player is activated after the draw
        game_data['deck'][-1]['color'] = 'BLUE'
        game_data['deck'][-1]['value'] = '7'
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        player = game_data['players'][0]
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)
        active_player = get_active_player(game_data)
        self.assertEqual(active_player, game_data['players'][1])

    def test_player_draw_card_does_not_advance_if_drawn_card_is_playable(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set top of deck to a matching card, to test that the first
        # player remains active after the draw
        game_data['deck'][-1]['color'] = 'RED'
        game_data['deck'][-1]['value'] = '1'
        # Set player's hand to not have a match, so the draw succeeds
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        save_state(game_data)
        player = game_data['players'][0]
        result = player_draw_card(game_data['id'], player['id'])
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertTrue(result)
        self.assertEqual(len(player['hand']), 4)
        active_player = get_active_player(game_data)
        # Ensure that the first player is still active
        self.assertEqual(active_player, game_data['players'][0])

    def test_player_draw_card_fails_if_player_has_playable_card(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to red card
        game_data['stack'][-1]['color'] = 'RED'
        # Ensure the player has a red card
        player = game_data['players'][0]
        player['hand'][0]['value'] = '5'
        player['hand'][0]['color'] = 'RED'
        save_state(game_data)
        result = player_draw_card(game_data['id'], player['id'])
        self.assertFalse(result)
        game_data = load_state(game_data['id'])
        player = game_data['players'][0]
        self.assertEqual(len(player['hand']), 7)

    def test_join_game(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        save_state(game_data)
        result = join_game(game_data['id'], 'PlayerTwo')
        self.assertIsNotNone(result)

    def test_join_game_defaults(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        save_state(game_data)
        result = join_game(game_data['id'], '')
        self.assertIsNotNone(result)
        game_data = load_state(game_data['id'])
        self.assertEqual(game_data['players'][1]['name'], DEFAULT_PLAYER_NAME)
        result = join_game(game_data['id'], None)
        self.assertIsNotNone(result)
        game_data = load_state(game_data['id'])
        self.assertEqual(game_data['players'][2]['name'], DEFAULT_PLAYER_NAME)

    def test_join_game_fails_when_game_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        save_state(game_data)
        result = join_game('bad_game_id', 'PlayerTwo')
        self.assertIsNone(result)

    def test_join_game_fails_when_game_is_already_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        save_state(game_data)
        result = join_game(game_data['id'], 'PlayerTwo')
        self.assertIsNone(result)

    def test_join_game_fails_when_game_is_over(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data['ended_at'] = 'sometime'
        save_state(game_data)
        result = join_game(game_data['id'], 'PlayerTwo')
        self.assertIsNone(result)

    def test_join_game_fails_when_max_players_reached(self):
        game_data = create_new_game('MyGame', 'PlayerOne', max_players=1)
        save_state(game_data)
        result = join_game(game_data['id'], 'PlayerTwo')
        self.assertIsNone(result)

    def test_leave_game(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        player2 = add_player_to_game(game_data, 'PlayerTwo')
        save_state(game_data)
        result = leave_game(game_data['id'], player2['id'])
        self.assertTrue(result)
        game_data = load_state(game_data['id'])
        self.assertFalse(game_data['ended_at'])
        self.assertEqual(len(game_data['players']), 1)

    def test_leave_game_fails_when_game_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        save_state(game_data)
        player = game_data['players'][0]
        result = leave_game('bad_game_id', player['id'])
        self.assertFalse(result)

    def test_leave_game_fails_when_player_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        save_state(game_data)
        player = game_data['players'][0]
        result = leave_game(game_data['id'], 'bad_player_id')
        self.assertFalse(result)

    def test_leave_game_fails_when_game_is_already_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        save_state(game_data)
        player = game_data['players'][0]
        result = leave_game(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_leave_game_fails_when_game_is_over(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        game_data['ended_at'] = 'sometime'
        save_state(game_data)
        player = game_data['players'][0]
        result = leave_game(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_leave_game_ends_when_admin_leaves(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        save_state(game_data)
        player = game_data['players'][0]
        result = leave_game(game_data['id'], player['id'])
        self.assertTrue(result)
        game_data = load_state(game_data['id'])
        self.assertTrue(game_data['ended_at'])

    def test_admin_start_game(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        save_state(game_data)
        player = game_data['players'][0]
        result = admin_start_game(game_data['id'], player['id'])
        self.assertTrue(result)

    def test_admin_start_game_fails_when_game_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        save_state(game_data)
        player = game_data['players'][0]
        result = admin_start_game('bad_game_id', player['id'])
        self.assertFalse(result)

    def test_admin_start_game_fails_when_player_id_not_valid(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        save_state(game_data)
        player = game_data['players'][0]
        result = admin_start_game(game_data['id'], 'bad_player_id')
        self.assertFalse(result)

    def test_admin_start_game_fails_when_game_id_already_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        start_game(game_data)
        save_state(game_data)
        player = game_data['players'][0]
        result = admin_start_game(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_admin_start_game_fails_when_game_is_over(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        game_data['ended_at'] = 'sometime'
        save_state(game_data)
        player = game_data['players'][0]
        result = admin_start_game(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_admin_start_game_fails_when_player_not_admin(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        add_player_to_game(game_data, 'PlayerTwo')
        player = game_data['players'][0]
        player['admin'] = False
        save_state(game_data)
        result = admin_start_game(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_admin_start_game_fails_when_min_players_not_reached(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        player = game_data['players'][0]
        save_state(game_data)
        result = admin_start_game(game_data['id'], player['id'])
        self.assertFalse(result)

    def test_player_has_matching_color_card_succeeds(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to red card
        game_data['stack'][-1]['color'] = 'RED'
        # Ensure the player has a red card
        player = game_data['players'][0]
        player['hand'][0]['value'] = '5'
        player['hand'][0]['color'] = 'RED'
        result = player_has_matching_color_card(game_data, player)
        self.assertTrue(result)

    def test_player_has_matching_color_card_fails(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an impossible color
        game_data['stack'][-1]['color'] = 'IMPOSSIBLE_COLOR_TO_MATCH'
        player = game_data['players'][0]
        result = player_has_matching_color_card(game_data, player)
        self.assertFalse(result)

    def test_player_has_playable_card_succeeds(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to have a match for the above card
        player['hand'] = []
        player['hand'].append(create_card('6', 'RED'))
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('7', 'BLUE'))
        result = player_has_playable_card(game_data, player)
        self.assertTrue(result)

    def test_player_has_playable_card_fails(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        start_game(game_data)
        # Set top of stack to an arbitrary card
        game_data['stack'][-1]['color'] = 'RED'
        game_data['stack'][-1]['value'] = '5'
        player = game_data['players'][0]
        # Set player's hand to not have the above card
        player['hand'] = []
        player['hand'].append(create_card('3', 'GREEN'))
        player['hand'].append(create_card('6', 'YELLOW'))
        player['hand'].append(create_card('7', 'BLUE'))
        result = player_has_playable_card(game_data, player)
        self.assertFalse(result)


if __name__ == '__main__':
    tests = unittest.TestLoader().loadTestsFromTestCase(GameTestCase)
    unittest.TextTestRunner(verbosity=2).run(tests)
