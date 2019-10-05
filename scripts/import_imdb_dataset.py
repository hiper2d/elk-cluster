#!/usr/bin/python
# encoding: utf-8

# The original script was taken from here: https://github.com/TetraTutorials/imdb_data_import_elastic
# IMDB datasets can be found here: https://www.imdb.com/interfaces/

import json


def get_or_empty(val):
    if val == '\\N':
        return ''
    return '[' + val + ']'


def get_movies_or_empty(movies_string, movies_dict):
    if movies_string == '\\N':
        return ''
    movie_tokens = movies_string.split(',')
    titles = []
    for movie_id in movie_tokens:
        titles.append(movies_dict[movie_id] if movie_id in movies_dict else 'unknown')
    return '[' + ','.join(titles) + ']'


def write_a_bulk_file(items):
    with open('../dataset/imdb.json', 'w') as f:
        lines = '\n'.join(items)
        lines += '\n'
        f.write(lines)


def main(actors, movies):
    actor_lines = actors.split('\n')
    movie_lines = movies.split('\n')
    actor_lines = actor_lines[1:-1]  # skip first line with headers and last empty line
    movie_lines = movie_lines[1:-1]

    movie_dict = {}
    for movie_line in movie_lines:
        movie_tokens = movie_line.split('\t')
        movie_dict[movie_tokens[0]] = movie_tokens[2]

    json_items = []
    for line in actor_lines:
        tokens = line.split('\t')

        primary_name = get_or_empty(tokens[1])
        birth_year = get_or_empty(tokens[2])
        death_year = get_or_empty(tokens[3])
        primary_profession = get_or_empty(tokens[4])
        known_for_titles = get_movies_or_empty(tokens[5], movie_dict)

        json_items.append(json.dumps({
            'primary_name': primary_name,
            'birth_year': birth_year,
            'death_year': death_year,
            'primary_profession': primary_profession,
            'known_for_titles': known_for_titles
        }))

    write_a_bulk_file(json_items)


if __name__ == '__main__':
    with open('../dataset/name.basics.tsv') as f:
        name_content = f.read()
    with open('../dataset/title.basics.tsv') as f:
        title_content = f.read()
    main(name_content, title_content)
