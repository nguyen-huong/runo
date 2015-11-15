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
        save_state(game_data)
        game_data = load_state(game_data['id'])
        self.assertNotEqual(game_data, {})

    def test_new_game_starts_with_108_cards(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertEqual(len(game_data['deck']), 108)

    def test_new_game_is_not_active(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertFalse(game_data['active'])

    def test_new_game_is_not_reversed(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        self.assertFalse(game_data['reverse'])

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
        player = add_player_to_game(game_data, 'PlayerTwo')
        player = add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        for player in game_data['players']:
            self.assertEqual(len(player['hand']), 7)

    def test_no_player_is_active_before_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        player = add_player_to_game(game_data, 'PlayerTwo')
        player = add_player_to_game(game_data, 'PlayerThree')
        for player in game_data['players']:
            self.assertFalse(player['active'])

    def test_admin_player_is_active_after_game_starts(self):
        game_data = create_new_game('MyGame', 'PlayerOne')
        player = add_player_to_game(game_data, 'PlayerTwo')
        player = add_player_to_game(game_data, 'PlayerThree')
        start_game(game_data)
        # admin_player =





if __name__ == '__main__':
    tests = unittest.TestLoader().loadTestsFromTestCase(GameTestCase)
    unittest.TextTestRunner(verbosity=2).run(tests)
