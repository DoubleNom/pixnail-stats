from pixnail import *


class PixnailUser:
    def __init__(self, pixnail: Pixnail, folder: str):
        self.cards = self._load_cards(os.path.join(folder, "cards.json"))
        self.boosters = self._load_boosters(os.path.join(folder, "boosters.json"))
        self.pseudo = self._load_username(os.path.join(folder, "user.json"))
        self.drop_rates = self._compute_card_expected_drop_rates(pixnail)

    @staticmethod
    def _load_cards(cards_filename):
        j_object = load_json_file(cards_filename)
        cards = {}
        for j_card in j_object:
            card, index, generation = Pixnail.Card.from_json(j_card)
            if generation not in cards:
                cards[generation] = {}
            cards[generation][index] = card
        return cards

    @staticmethod
    def _load_boosters(boosters_filename):
        j_object = load_json_file(boosters_filename)
        boosters = {}
        for j_booster in j_object:
            j_generation = j_booster["generationId"]
            j_type = j_booster["boosterId"]
            generation = Pixnail.Generation.from_string(j_generation)
            kind = Pixnail.Booster.Kind.from_string(j_type)
            count = j_booster["quantity"]
            if generation not in boosters:
                boosters[generation] = {}
            boosters[generation][kind] = count
        return boosters

    @staticmethod
    def _load_username(filename: str):
        j_object = load_json_file(filename)
        return j_object["pseudo"]

    def _compute_card_expected_drop_rates(self, pixnail: Pixnail):
        generations = [Pixnail.Generation.origin]
        rarities = [Pixnail.Card.Rarity.s, Pixnail.Card.Rarity.a, Pixnail.Card.Rarity.b, Pixnail.Card.Rarity.c,
                    Pixnail.Card.Rarity.d]
        shinies = [Pixnail.Card.Shiny.normal, Pixnail.Card.Shiny.shiny, Pixnail.Card.Shiny.super_shiny]
        kinds = [Pixnail.Booster.Kind.normal, Pixnail.Booster.Kind.premium]

        generation_rarity_count = {}
        for generation in generations:
            generation_rarity_count[generation] = {}
            for rarity in rarities:
                cards = list(filter(lambda i: pixnail.cards[generation][i].rarity == rarity, pixnail.cards[generation]))
                generation_rarity_count[generation][rarity] = len(cards)

        booster_ratio = {}
        for generation in generations:
            booster_ratio[generation] = {}
            cards = 0
            for kind in kinds:
                cards = cards + self.boosters[generation][kind] * pixnail.boosters[generation][
                    kind].card_count
            for kind in kinds:
                booster_ratio[generation][kind] = self.boosters[generation][kind] * pixnail.boosters[generation][
                    kind].card_count / cards

        expected_drop_rates = {}
        total_sum = 0
        for generation in generations:
            expected_drop_rates[generation] = {}
            for rarity in rarities:
                expected_drop_rates[generation][rarity] = {}
                for shiny in shinies:
                    card_rates = {}
                    for kind in kinds:
                        booster = pixnail.boosters[generation][kind]
                        rarity_rate = booster.rarity_drop_rates[rarity] / booster.rarity_drop_rates[
                            Pixnail.Card.Rarity.total]
                        shiny_rate = booster.shiny_drop_rates[shiny] / booster.shiny_drop_rates[
                            Pixnail.Card.Shiny.total]
                        card_rates[kind] = rarity_rate * shiny_rate * booster_ratio[generation][kind]
                    expected_drop_rates[generation][rarity][shiny] = sum(card_rates.values()) / generation_rarity_count[generation][rarity]
                    total_sum = total_sum + expected_drop_rates[generation][rarity][shiny] * generation_rarity_count[generation][rarity]
        return expected_drop_rates

    def get_card_expected_drop_rate(self, generation: Pixnail.Generation, rarity: Pixnail.Card.Rarity,
                                    shiny: Pixnail.Card.Shiny):
        if generation == Pixnail.Generation.promo:
            return 0
        return self.drop_rates[generation][rarity][shiny]
