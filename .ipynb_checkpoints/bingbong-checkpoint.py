import itertools
import pprint
from math import ceil
from numpy import dot
from IPython.display import clear_output
from tqdm.notebook import tqdm


with open("commonWords.txt") as f:
    COM_WORDS = set(word.strip() for word in f.readlines())


DEFAULT_SCORES = {'A': 5, 'B': 40, 'C': 35, 'D': 30, 'E': 5, 'F': 50, 'G': 45, 'H': 40, 'I': 9, 'J': 75, 'K': 50, 'L': 9, 'M': 35, 'N': 25, 'O': 7, 'P': 35, 'Q': 85, 'R': 7, 'S': 5, 'T': 9, 'U': 15, 'V': 85, 'W': 70, 'X': 95, 'Y': 40, 'Z': 100}


def get_tiles(curr_set=[]):
    pprint.pp(curr_set)
    letter = input("Letter? (done to finish)").upper()
    if letter == "DONE":
        return curr_set
    score = int(input(f"Letter Score? Default={DEFAULT_SCORES.get(letter)}: ") or DEFAULT_SCORES.get(letter))
    count = int(input(f"Letter Count? Default=1: ") or 1)
    curr_set.append((letter, score, count))
    
    clear_output()
    return get_tiles(curr_set)


def get_pseudo_candidates(candidates, max_length, perfect_length=False):
    if perfect_length:
        return [cand for cand in candidates if len(cand) == max_length]
    all_candidates = []
    for cand in candidates:
        if len(cand) == max_length: all_candidates.append(cand)
        if len(cand) == max_length - 1:
            all_candidates.append([" "]+list(cand))
            all_candidates.append(list(cand)+[" "])
        if len(cand) == max_length - 2:
            all_candidates.append([" "]+list(cand)+[" "])
            all_candidates.append(list(cand)+[" "]+[" "])
            all_candidates.append([" "]+[" "]+list(cand))
    return all_candidates


def get_words(tile_dict, use_blank):
    letter_list = "".join([letter*tile_dict[letter] for letter in tile_dict])
    base_word_candidates = set(word for n in (5, 4, 3) for word in itertools.permutations(letter_list, n)
                       if "".join(word) in COM_WORDS)
    blank_candidates = set()
    if use_blank:
        for letter in tqdm("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            letter_list_copy = "".join(list(letter_list) + [letter])
            new_word_candidates = set(word for n in (5, 4, 3) for word in itertools.permutations(letter_list_copy, n)
                       if "".join(word) in COM_WORDS and word not in base_word_candidates)
            
            for word in new_word_candidates:
                for i, l in enumerate(word):
                    if l == letter:
                        temp_word = list(word)
                        temp_word[i] = l.lower()
                        blank_candidates.add(tuple(temp_word))
        
    return base_word_candidates | blank_candidates


def get_best_words(
        letters, 
        used_letters="", 
        fixed_slots=None, 
        max_length=5,
        doubles=None,
        triple=None, 
        perfect_length=False, 
        use_blank=False,
        topn=30
):
    if not fixed_slots:
        fixed_slots = [None] * max_length
    mults = [1] * max_length  
    if doubles:
        if type(doubles) == list:
            for d in doubles:
                mults[d] = 2
        else:
            mults[doubles] = 2
    if triple:
        mults[triple] = 3
    if len(mults) != max_length or len(fixed_slots) != max_length:
        return "check length of inputs"
    tile_dict = {letter:count for letter, score, count in letters}
    for letter in used_letters:
        tile_dict[letter] -= 1
    candidates = get_words(tile_dict, use_blank)
    score_dict = {letter: score for letter, score, count in letters}
    all_candidates = get_pseudo_candidates(candidates, max_length, perfect_length)
    for i, letter in enumerate(fixed_slots):
        if letter != None:
            all_candidates = [cand for cand in all_candidates if cand[i] == letter]
    total_scores = sorted([(cand, ceil(dot([score_dict.get(letter, 0) for letter in cand], mults)*1.3)) 
                           for cand in all_candidates], key=lambda x: -x[1])
    return total_scores[:topn]