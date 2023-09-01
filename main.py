from pixnail import Pixnail
from pixnail_user import PixnailUser
from xlsxwriter import Workbook, worksheet


def write_boosters(pixnail: Pixnail, user: PixnailUser, row: int, ws: worksheet) -> int:
    ws.merge_range(f"A{row}:D{row}", "Boosters")
    ws.merge_range(f"E{row}:I{row}", "Rarity drop rate")
    ws.merge_range(f"J{row}:L{row}", "Shiny drop rate")
    row = row + 1
    ws.write(f"A{row}", "Generation")
    ws.write(f"B{row}", "Kind")
    ws.write(f"C{row}", "Count")
    ws.write(f"D{row}", "Shells")
    ws.write(f"E{row}", "S")
    ws.write(f"F{row}", "A")
    ws.write(f"G{row}", "B")
    ws.write(f"H{row}", "C")
    ws.write(f"I{row}", "D")
    ws.write(f"J{row}", "Giga")
    ws.write(f"K{row}", "Super")
    ws.write(f"L{row}", "Normal")
    row = row + 1

    total_price = 0
    for generation, kind in [
        [Pixnail.Generation.origin, Pixnail.Booster.Kind.normal],
        [Pixnail.Generation.origin, Pixnail.Booster.Kind.premium],
        [Pixnail.Generation.promo, Pixnail.Booster.Kind.normal],
        [Pixnail.Generation.promo, Pixnail.Booster.Kind.drop]
    ]:
        booster_count = user.boosters[generation][kind]
        price = booster_count * pixnail.boosters[generation][kind].price
        total_price = total_price + price
        ws.write(f"A{row}", generation.name)
        ws.write(f"B{row}", kind.name)
        ws.write(f"C{row}", booster_count)
        ws.write(f"D{row}", price)
        pixnail_booster = pixnail.boosters[generation][kind]
        for [letter, rarity] in [
            ["E", Pixnail.Card.Rarity.s],
            ["F", Pixnail.Card.Rarity.a],
            ["G", Pixnail.Card.Rarity.b],
            ["H", Pixnail.Card.Rarity.c],
            ["I", Pixnail.Card.Rarity.d],
        ]:
            ws.write(f"{letter}{row}", pixnail_booster.rarity_drop_rates[rarity] / pixnail_booster.rarity_drop_rates[
                Pixnail.Card.Rarity.total] * 100)
        for [letter, shiny] in [
            ["J", Pixnail.Card.Shiny.super_shiny],
            ["K", Pixnail.Card.Shiny.shiny],
            ["L", Pixnail.Card.Shiny.normal]
        ]:
            ws.write(f"{letter}{row}", pixnail_booster.shiny_drop_rates[shiny] / pixnail_booster.shiny_drop_rates[
                Pixnail.Card.Shiny.total] * 100)
        row = row + 1
    ws.write(f"C{row}", "Total")
    ws.write(f"D{row}", total_price)

    return row + 1


def write_cards(pixnail: Pixnail, user: PixnailUser, row: int, ws: worksheet):
    ws.merge_range(f"A{row}:C{row}", "Cards")
    ws.merge_range(f"D{row}:F{row}", "Count")
    ws.merge_range(f"G{row}:I{row}", "Drop rate")
    ws.merge_range(f"J{row}:L{row}", "Expected rate")
    ws.merge_range(f"M{row}:O{row}", "Diff")
    row = row + 1
    ws.write(f"A{row}", "Generation")
    ws.write(f"B{row}", "Rarity")
    ws.write(f"C{row}", "Index")
    for [letter, text] in [
        ["D", "Normal"],
        ["E", "Puddy"],
        ["F", "Giga"],
    ]:
        ws.write(f"{letter}{row}", text)
        ws.write(f"{chr(ord(letter) + 3)}{row}", text)
        ws.write(f"{chr(ord(letter) + 6)}{row}", text)
        ws.write(f"{chr(ord(letter) + 9)}{row}", text)
    row = row + 1
    total_cards = {
        Pixnail.Generation.origin: 0,
        Pixnail.Generation.promo: 0,
    }

    for generation in [Pixnail.Generation.origin, Pixnail.Generation.promo]:
        for index in range(0, len(pixnail.cards[generation])):
            if index not in user.cards[generation]: continue
            total_cards[generation] = total_cards[generation] + sum(user.cards[generation][index].quantities.values())

    for generation in [Pixnail.Generation.origin, Pixnail.Generation.promo]:
        for index in range(0, len(pixnail.cards[generation])):
            if index not in user.cards[generation]: continue
            card = user.cards[generation][index]
            total = sum(user.cards[generation][index].quantities.values())
            ws.write(f'A{row}', generation.name)
            ws.write(f'B{row}', pixnail.cards[generation][index].rarity.name)
            ws.write(f'C{row}', index)
            ws.write(f'D{row}', card.quantities[Pixnail.Card.Shiny.normal])
            ws.write(f'E{row}', card.quantities[Pixnail.Card.Shiny.shiny])
            ws.write(f'F{row}', card.quantities[Pixnail.Card.Shiny.super_shiny])
            for [letter, shiny] in [
                ['G', Pixnail.Card.Shiny.normal],
                ['H', Pixnail.Card.Shiny.shiny],
                ['I', Pixnail.Card.Shiny.super_shiny]
            ]:
                user_drop_rate = card.quantities[shiny] / total_cards[generation]
                expected_drop_rate = user.get_card_expected_drop_rate(generation, card.rarity, shiny)
                ws.write(f'{chr(ord(letter))}{row}', user_drop_rate)
                ws.write(f'{chr(ord(letter) + 3)}{row}', expected_drop_rate)
                if expected_drop_rate == 0: continue
                diff = abs(user_drop_rate - expected_drop_rate) / expected_drop_rate * 100
                ws.write(f'{chr(ord(letter) + 6)}{row}', diff)
            row = row + 1
    return row + 1


def main():
    pixnail = Pixnail(folder="data")
    user = PixnailUser(pixnail, folder="data")
    wb = Workbook(f"{user.pseudo}.xslx")
    ws = wb.add_worksheet()
    row = write_boosters(pixnail, user, 1, ws)
    row = write_cards(pixnail, user, row + 1, ws)

    wb.close()


if __name__ == "__main__":
    main()
