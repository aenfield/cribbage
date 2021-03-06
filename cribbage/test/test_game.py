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

    # def test_game_has_play(self):
    #     sut = game.Game()
    #     sut.play()


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

    def test_player_get_crib_cards_fails_when_at_least_one_card_doesnt_exist_in_hand(self):
        sut = game.UIPlayer(input_func = lambda x: 'JS,4S')
        sut.hand = cards.Deck().draw_hand(6)
        with pytest.raises(ValueError):
            no_crib_cards = sut.get_crib_cards()

    def test_player_get_crib_cards_removes_crib_cards_from_hand(self):
        sut = game.UIPlayer(input_func = lambda x: '3S,AS')
        sut.hand = cards.Deck().draw_hand(6)
        crib_cards = sut.get_crib_cards()
        assert len(sut.hand) == 4
        assert cards.Card.from_spec('3S') not in sut.hand
        assert cards.Card.from_spec('AS') not in sut.hand