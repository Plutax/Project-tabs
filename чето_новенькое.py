from music21 import stream, note, chord, meter, key

#словарь для перевода гитарных нот в фортепианные (16 ладов)
guitar_to_piano = {
    (1, 0): 'E4', (1, 1): 'F4', (1, 2): 'F#4', (1, 3): 'G4', (1, 4): 'G#4', (1, 5): 'A4',
    (1, 6): 'A#4', (1, 7): 'B4', (1, 8): 'C5', (1, 9): 'C#5', (1, 10): 'D5', (1, 11): 'D#5',
    (1, 12): 'E5', (1, 13): 'F5', (1, 14): 'F#5', (1, 15): 'G5', (1, 16): 'G#5',
    (2, 0): 'B3', (2, 1): 'C4', (2, 2): 'C#4', (2, 3): 'D4', (2, 4): 'D#4', (2, 5): 'E4',
    (2, 6): 'F4', (2, 7): 'F#4', (2, 8): 'G4', (2, 9): 'G#4', (2, 10): 'A4', (2, 11): 'A#4',
    (2, 12): 'B4', (2, 13): 'C5', (2, 14): 'C#5', (2, 15): 'D5', (2, 16): 'D#5',
    (3, 0): 'G3', (3, 1): 'G#3', (3, 2): 'A3', (3, 3): 'A#3', (3, 4): 'B3', (3, 5): 'C4',
    (3, 6): 'C#4', (3, 7): 'D4', (3, 8): 'D#4', (3, 9): 'E4', (3, 10): 'F4', (3, 11): 'F#4',
    (3, 12): 'G4', (3, 13): 'G#4', (3, 14): 'A4', (3, 15): 'A#4', (3, 16): 'B4',
    (4, 0): 'D3', (4, 1): 'D#3', (4, 2): 'E3', (4, 3): 'F3', (4, 4): 'F#3', (4, 5): 'G3',
    (4, 6): 'G#3', (4, 7): 'A3', (4, 8): 'A#3', (4, 9): 'B3', (4, 10): 'C4', (4, 11): 'C#4',
    (4, 12): 'D4', (4, 13): 'D#4', (4, 14): 'E4', (4, 15): 'F4', (4, 16): 'F#4',
    (5, 0): 'A2', (5, 1): 'A#2', (5, 2): 'B2', (5, 3): 'C3', (5, 4): 'C#3', (5, 5): 'D3',
    (5, 6): 'D#3', (5, 7): 'E3', (5, 8): 'F3', (5, 9): 'F#3', (5, 10): 'G3', (5, 11): 'G#3',
    (5, 12): 'A3', (5, 13): 'A#3', (5, 14): 'B3', (5, 15): 'C4', (5, 16): 'C#4',
    (6, 0): 'E2', (6, 1): 'F2', (6, 2): 'F#2', (6, 3): 'G2', (6, 4): 'G#2', (6, 5): 'A2',
    (6, 6): 'A#2', (6, 7): 'B2', (6, 8): 'C3', (6, 9): 'C#3', (6, 10): 'D3', (6, 11): 'D#3',
    (6, 12): 'E3', (6, 13): 'F3', (6, 14): 'F#3', (6, 15): 'G3', (6, 16): 'G#3'
}


def parse_input(user_input):
    parts = user_input.split()
    num_notes = int(parts[0][:-1])
    notes = []
    for i in range(num_notes):
        string = int(parts[1 + 2 * i])
        fret = int(parts[2 + 2 * i])
        if (string, fret) in guitar_to_piano:
            notes.append(guitar_to_piano[(string, fret)])
        else:
            print(f"err: нота на струне {string}, лад {fret} не найдена в словаре:(")
    return notes


def create_score(num_bars):
    score = stream.Score()
    part = stream.Part()
    for _ in range(num_bars):
        bar = stream.Measure()
        bar.append(key.KeySignature(0))
        part.append(bar)
    score.append(part)
    return score


def main():
    num_bars = int(input("количество тактов: "))
    score = create_score(num_bars)

    for i in range(num_bars):
        print(f"ноты {i + 1}-го такта:")
        while True:
            user_input = input()
            if user_input.lower() == 'end':
                break
            notes = parse_input(user_input)
            if len(notes) == 1:
                n = note.Note(notes[0])
            else:
                n = chord.Chord(notes)
            score.parts[0].measures(i, i + 1)[0].append(n)

    # экспорт в musicXML
    score.write('musicxml', fp='output.mxl')
    print(" партитура сохранена в файлы output.mxl")


if __name__ == "__main__":
    main()