from enum import Enum
import os
from json_file import load_json_file


class Pixnail:
    class Generation(Enum):
        origin = 1
        promo = 2

        @staticmethod
        def from_string(name: str):
            if name == "origin":
                return Pixnail.Generation.origin
            elif name == "promo":
                return Pixnail.Generation.promo
            else:
                raise RuntimeError(f"Unknown generation {name}")

    class Card:
        class Rarity(Enum):
            total = 0
            d = 1
            c = 2
            b = 3
            a = 4
            s = 5

            def to_string(self):
                return self.name

            @staticmethod
            def from_string(name: str):
                if name == "total":
                    return Pixnail.Card.Rarity.total
                elif name == "d":
                    return Pixnail.Card.Rarity.d
                elif name == "c":
                    return Pixnail.Card.Rarity.c
                elif name == "b":
                    return Pixnail.Card.Rarity.b
                elif name == "a":
                    return Pixnail.Card.Rarity.a
                elif name == "s":
                    return Pixnail.Card.Rarity.s
                else:
                    raise RuntimeError(f"Unknown card rarity {name}")

        class Shiny(Enum):
            total = 0
            normal = 1
            shiny = 2
            super_shiny = 3

            def to_string(self):
                if self == Pixnail.Card.Shiny.total:
                    return "total"
                elif self == Pixnail.Card.Shiny.normal:
                    return "normal"
                elif self == Pixnail.Card.Shiny.shiny:
                    return "shiny"
                elif self == Pixnail.Card.Shiny.super_shiny:
                    return "superShiny"
                else:
                    raise RuntimeError(f"Unknown shiny {self}")

            @staticmethod
            def from_string(name: str):
                if name == "total":
                    return Pixnail.Card.Shiny.total
                elif name == "normal":
                    return Pixnail.Card.Shiny.normal
                elif name == "shiny":
                    return Pixnail.Card.Shiny.shiny
                elif name == "superShiny":
                    return Pixnail.Card.Shiny.super_shiny
                else:
                    raise RuntimeError(f"Unknown card shinyness {name}")

        def __init__(self, rarity: Rarity, quantities: dict):
            self.rarity = rarity
            self.quantities = quantities

        @staticmethod
        def from_json(j_object: dict):
            rarity = Pixnail.Card.Rarity.from_string(j_object["rarity"])
            index = j_object["index"]
            generation = Pixnail.Generation.from_string(j_object["generationId"])
            quantities = {
                Pixnail.Card.Shiny.total: 0,
                Pixnail.Card.Shiny.normal: 0,
                Pixnail.Card.Shiny.shiny: 0,
                Pixnail.Card.Shiny.super_shiny: 0,
            }
            if "quantities" in j_object:
                j_quantities = j_object["quantities"]
                for j_quantity in j_quantities:
                    quantity = Pixnail.Card.Shiny.from_string(j_quantity)
                    quantities[quantity] = j_quantities[j_quantity]
            return [
                Pixnail.Card(
                    rarity=rarity,
                    quantities=quantities
                ),
                index,
                generation,
            ]

    class Booster:
        class Kind(Enum):
            normal = 1
            premium = 2
            drop = 3

            @staticmethod
            def from_string(name: str):
                if name == "normal":
                    return Pixnail.Booster.Kind.normal
                elif name == "premium":
                    return Pixnail.Booster.Kind.premium
                elif name == "drop":
                    return Pixnail.Booster.Kind.drop
                else:
                    raise RuntimeError(f"Unknown booster type {name}")

        class PromoDrop(Enum):
            total = 0
            none = 1
            one = 2
            two = 3

            def to_string(self):
                if self == self.total:
                    return "total"
                elif self == self.none:
                    return "none"
                elif self == self.one:
                    return "oneCard"
                elif self == self.two:
                    return "twoCards"
                else:
                    raise RuntimeError(f"Unknown promo drop {self}")

            @staticmethod
            def from_string(name: str):
                if name == "total":
                    return Pixnail.Booster.PromoDrop.total
                elif name == "none":
                    return Pixnail.Booster.PromoDrop.none
                elif name == "oneCard":
                    return Pixnail.Booster.PromoDrop.one
                elif name == "twoCards":
                    return Pixnail.Booster.PromoDrop.two
                else:
                    raise RuntimeError(f"Unknown booster promo drop {name}")

        def __init__(self, shiny_drop_rates: dict, rarity_drop_rates: dict, promo_drop_rates: dict, card_count: int,
                     price: int):
            self.shiny_drop_rates = shiny_drop_rates
            self.rarity_drop_rates = rarity_drop_rates
            self.promo_drop_rates = promo_drop_rates
            self.card_count = card_count
            self.price = price

        @staticmethod
        def from_json(j_object: dict):
            shiny_drop_rates = {}
            rarity_drop_rates = {}
            promo_drop_rates = {}

            j_shiny_drop = j_object["shinyDrop"]
            for shiny_drop in [Pixnail.Card.Shiny.super_shiny, Pixnail.Card.Shiny.shiny, Pixnail.Card.Shiny.total]:
                shiny_drop_rates[shiny_drop] = j_shiny_drop[shiny_drop.to_string()]
            shiny_drop_rates[Pixnail.Card.Shiny.normal] = shiny_drop_rates[Pixnail.Card.Shiny.total] * 2 - sum(
                shiny_drop_rates.values())

            j_rarity_drop = j_object["rarityDrop"]
            for rarity_drop in [Pixnail.Card.Rarity.s, Pixnail.Card.Rarity.a, Pixnail.Card.Rarity.b,
                                Pixnail.Card.Rarity.c, Pixnail.Card.Rarity.total, ]:
                rarity_drop_rates[rarity_drop] = j_rarity_drop[rarity_drop.to_string()]
            rarity_drop_rates[Pixnail.Card.Rarity.d] = rarity_drop_rates[Pixnail.Card.Rarity.total] * 2 - sum(
                rarity_drop_rates.values())

            if "promoDrop" in j_object:
                j_promo_drop = j_object["promoDrop"]
                for promo_drop in [Pixnail.Booster.PromoDrop.one, Pixnail.Booster.PromoDrop.two,
                                   Pixnail.Booster.PromoDrop.total, ]:
                    promo_drop_rates[promo_drop] = j_promo_drop[promo_drop.to_string()]
                promo_drop_rates[Pixnail.Booster.PromoDrop.none] = promo_drop_rates[
                                                                       Pixnail.Booster.PromoDrop.total] * 2 - sum(
                    promo_drop_rates.values())
            else:
                promo_drop_rates = {
                    Pixnail.Booster.PromoDrop.none: 1,
                    Pixnail.Booster.PromoDrop.one: 0,
                    Pixnail.Booster.PromoDrop.two: 0,
                    Pixnail.Booster.PromoDrop.total: 1,
                }

            card_count = j_object["cardsQuantity"]
            price = j_object["prices"]["shells"]

            kind = Pixnail.Booster.Kind.from_string(j_object["name"])

            return [Pixnail.Booster(
                shiny_drop_rates=shiny_drop_rates,
                rarity_drop_rates=rarity_drop_rates,
                promo_drop_rates=promo_drop_rates,
                card_count=card_count,
                price=price
            ), kind]

    def __init__(self, folder):
        self.cards, self.boosters = Pixnail._load_generation(os.path.join(folder, "generations.json"))

    @staticmethod
    def _load_generation(generation_file: str):
        j_object = load_json_file(generation_file)
        return Pixnail._load_cards(j_object), Pixnail._load_boosters(j_object)

    @staticmethod
    def _load_cards(j_object: dict):
        cards = {}
        for j_generation in j_object:
            cards[Pixnail.Generation.from_string(j_generation["id"])] = {}
            j_cards = j_generation["cards"]
            for j_card in j_cards:
                card, index, generation = Pixnail.Card.from_json(j_card)
                cards[generation][index] = card
        return cards

    @staticmethod
    def _load_boosters(j_object: dict):
        boosters = {}
        for j_generation in j_object:
            generation = Pixnail.Generation.from_string(j_generation["id"])
            boosters[generation] = {}
            j_boosters = j_generation["boosters"]
            for j_booster in j_boosters:
                booster, kind = Pixnail.Booster.from_json(j_booster)
                boosters[generation][kind] = booster
        return boosters
