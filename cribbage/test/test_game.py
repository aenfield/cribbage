import game
import cards

import pytest

class TestGame:
    def test_game_has_players(self):
        sut = game.Game()
        assert sut.player_one.name == "Player 1"
        assert sut.player_two.name == "Player 2"

    def test_game_has_deck(self):
        sut = game.Game()
        assert len(sut.deck) == 52

    def test_game_prints_status(self):
        sut = game.Game()
        status = sut.status()
        assert "Player 1" in status
        assert "Player 2" in status
        assert "hand" in status
        assert "None" in status # haven't drawn a hand so the hand text will say 'None'
        assert "Cut card" in status

    def test_game_can_cut_card(self):
        sut = game.Game()
        sut.cut_cards()
        assert isinstance(sut.cut_card, cards.Card)

    def test_score_cards_no_crib(self):
        sut = game.Game()
        sut.player_one.hand = cards.Hand.from_specs(['2C','3S','3C','8D'])
        sut.update_player_score(sut.player_one)
        assert sut.player_one.score == 2

    def test_score_cards_crib(self):
        sut = game.Game()
        sut.crib = cards.Hand.from_specs(['2C','3S','3C','8D'])
        sut.update_player_score(sut.player_one, crib=True)
        assert sut.player_one.score == 2

    def test_score_cards_says_when_player_wins(self):
        sut = game.Game(score_to_win=1)
        sut.player_one.hand = cards.Hand.from_specs(['2C','3S','3C','8D'])
        with pytest.raises(game.WinningScoreException):
            sut.update_player_score(sut.player_one)

    def test_game_has_crib_and_non_crib_players(self):
        sut = game.Game()
        assert sut.player_one is sut.crib_player
        assert sut.player_two is sut.non_crib_player

    def test_can_swap_crib_player(self):
        sut = game.Game()
        sut.swap_crib_player()
        assert sut.player_two is sut.crib_player
        assert sut.player_one is sut.non_crib_player 

    def test_single_play_card_is_appended(self):
        sut = game.Game()
        sut.player_one.hand = cards.Hand.from_specs(['2C','3S','3C','8D'])
        sut.player_one.reset_eligible_play_cards()
        curr_play_cards, all_play_cards = [], []
        sut.get_and_score_one_play_card(sut.player_one, curr_play_cards, all_play_cards)
        assert len(curr_play_cards) == 1
        assert len(all_play_cards) == 0

    def test_get_and_score_play_card_scores_nothing_with_first_card(self):
        sut = game.Game(game.UIPlayer(input_func = lambda x: '5S'))
        sut.player_one.hand = cards.Hand.from_specs(['2C','5S','3C','8D'])
        sut.player_one.reset_eligible_play_cards()
        curr_play_cards = []
        sut.get_and_score_one_play_card(sut.player_one, curr_play_cards, [])
        assert sut.player_one.score == 0
        assert len(curr_play_cards) == 1
        assert curr_play_cards[0] == cards.Card.from_spec('5S')

    def test_get_and_score_play_card_scores_second_card(self):
        sut = game.Game(game.UIPlayer(input_func = lambda x: '5S'))
        sut.player_one.hand = cards.Hand.from_specs(['2C','5S','3C','8D'])
        sut.player_one.reset_eligible_play_cards()
        curr_play_cards, all_play_cards = [cards.Card.from_spec('KD')], []
        sut.get_and_score_one_play_card(sut.player_one, curr_play_cards, all_play_cards)
        assert sut.player_one.score == 2
        assert len(curr_play_cards) == 2
        assert curr_play_cards[1] == cards.Card.from_spec('5S')
        assert len(all_play_cards) == 0

    def test_get_and_score_play_card_sets_said_go(self):
        sut = game.Game()
        sut.player_one.hand = cards.Hand()
        sut.player_one.reset_eligible_play_cards()
        assert sut.player_one.said_go == False
        sut.get_and_score_one_play_card(sut.player_one, [], [])
        assert sut.player_one.said_go == True

    def test_get_other_player_simply_swaps(self):
        sut = game.Game()
        assert sut._get_other_player(sut.player_one) is sut.player_two
        assert sut._get_other_player(sut.player_two) is sut.player_one

    def test_get_next_player_for_play_swaps_if_no_go(self):
        sut = game.Game()
        next_player = sut._get_next_player_for_play(sut.player_one)
        assert next_player is sut.player_two
        next_player_two = sut._get_next_player_for_play(sut.player_two)
        assert next_player_two is sut.player_one

    def test_get_next_player_for_play_doesnt_swap_if_go(self):
        sut = game.Game()
        sut.player_two.said_go = True
        next_player = sut._get_next_player_for_play(sut.player_one)
        assert next_player is sut.player_one


class TestPlayer:
    def test_player_has_score(self):
        sut = game.Player()
        assert sut.score == 0

    def test_player_has_hand(self):
        sut = game.Player()
        assert sut.hand is None

    def test_player_prints_status(self):
        sut = game.Player()
        sut.hand = cards.Deck().draw_hand(6)
        status = sut.status()
        assert sut.name in status
        assert "0" in status # score
        assert "hand" in status
        assert "2" in status # there's a 2 card
        assert "crib" not in status

    def test_player_has_crib_property_and_status_shows_crib(self):
        sut = game.Player(crib=True)
        status = sut.status()
        assert "crib" in status

    def test_player_get_crib_cards_returns_two_cards(self):
        sut = game.Player()
        sut.hand = cards.Deck().draw_hand(6)
        crib_cards = sut.get_crib_cards()
        assert len(crib_cards) == 2
        assert crib_cards[0] == cards.Card.from_spec('AS')
        assert crib_cards[1] == cards.Card.from_spec('2S')

    def test_can_create_player_UI_instance(self):
        sut = game.UIPlayer()

    def test_player_uses_injected_func_for_input_and_defines_crib_cards(self):
        # ideally I could test the injected func separate from anything, but I can't think how now, 
        # so I'll test it with crib_cards - using the defined func/text to select a diff set of cards
        sut = game.UIPlayer(input_func = lambda x: '3S, 5S')
        sut.hand = cards.Deck().draw_hand(6)
        crib_cards = sut.get_crib_cards()
        assert len(crib_cards) == 2
        assert crib_cards[0] == cards.Card.from_spec('3S')
        assert crib_cards[1] == cards.Card.from_spec('5S')

    # we now ask repeatedly until we get a card that does exist
    # def test_player_get_crib_cards_fails_when_at_least_one_card_doesnt_exist_in_hand(self):
    #     sut = game.UIPlayer(input_func = lambda x: 'JS,4S')
    #     sut.hand = cards.Deck().draw_hand(6)
    #     with pytest.raises(ValueError):
    #         no_crib_cards = sut.get_crib_cards()

    def test_player_get_crib_cards_removes_crib_cards_from_hand(self):
        sut = game.UIPlayer(input_func = lambda x: '3S,AS')
        sut.hand = cards.Deck().draw_hand(6)
        crib_cards = sut.get_crib_cards()
        assert len(sut.hand) == 4
        assert cards.Card.from_spec('3S') not in sut.hand
        assert cards.Card.from_spec('AS') not in sut.hand

    def test_player_knows_winning_score(self):
        sut = game.Player()
        assert sut._score_to_win == 120
        sut2 = game.Player(score_to_win = 1)
        assert sut2._score_to_win == 1

    def test_player_score_doesnt_throw_win_exception_without_winning_score(self):
        sut = game.Player()
        sut.score = 119

    def test_player_score_throws_win_exception_when_winning_score_is_achieved(self):
        sut = game.Player(score_to_win=50)
        with pytest.raises(game.WinningScoreException):
            sut.score = 50

        sut2 = game.Player()
        with pytest.raises(game.WinningScoreException):
            sut.score = 120

    def test_player_get_play_card_returns_a_single_card(self):
        sut = game.Player()
        sut.hand = cards.Deck().draw_hand(4)
        sut.reset_eligible_play_cards()
        play_card = sut.get_play_card([], [])
        assert play_card == cards.Card.from_spec('AS')
        assert len(sut.remaining_cards_for_the_play) == 3

    def test_player_uses_injected_func_for_input_and_defines_play_card(self):
        sut = game.UIPlayer(input_func = lambda x: '2S')
        sut.hand = cards.Deck().draw_hand(4)
        sut.reset_eligible_play_cards()
        play_card = sut.get_play_card([], [])
        assert play_card == cards.Card.from_spec('2S')
        assert len(sut.remaining_cards_for_the_play) == 3

    # no longer need this test because we now keep asking forever if someone specifies a non-existent card
    # this hung VS Code, but running 'pytest --full-trace' from a cmd prompt let me kill pytest with a ctrl-c
    # and get a stack trace that showed exactly what test was causing the problem
    # def test_player_get_play_card_fails_when_card_doesnt_exist_in_eligible_cards(self):
    #     sut = game.UIPlayer(input_func = lambda x: 'KS')
    #     sut.hand = cards.Deck().draw_hand(4)
    #     sut.reset_eligible_play_cards()
    #     with pytest.raises(ValueError):
    #         no_play_card = sut.get_play_card([], [])
    
    def test_player_get_play_card_says_go_with_no_eligible_cards(self):
        sut = game.Player()
        sut.hand = cards.Hand()
        sut.reset_eligible_play_cards()
        play_card = sut.get_play_card([], [])
        assert play_card is None

    def test_player_get_play_card_says_go_when_no_cards_fit(self):
        sut = game.Player()
        sut.hand = cards.Hand.from_specs(['7C','8C','9D','QS'])
        sut.reset_eligible_play_cards()
        play_card = sut.get_play_card(cards.Hand.from_specs(['KC','KS','5D']), [])
        assert play_card is None

    def test_player_get_play_wont_select_card_that_exceeds_31(self):
        sut = game.RandomPlayer()
        sut.hand = cards.Hand.from_specs(['AS','KS'])
        sut.reset_eligible_play_cards()
        play_card = sut.get_play_card(cards.Hand.from_specs(['KD','KC','KH']), []) # so count is 30 - Ace is ok, but nothing else
        assert play_card == cards.Card.from_spec('AS')
        # to test I use a RandomPlayer with two cards in the hand: one that's ok and one that's not
        # it may take a few random choices before it'll get the one that's ok; the fact that this test
        # is then non-deterministic means that on average it'll pass ~50% of the time even if there's no
        # check for invalid choices... not sure how to get around this (one answer is to test other parts
        # of the call chain, and I am already doing that)
