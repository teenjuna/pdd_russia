#!/usr/bin/env python3

import os
import json
import argparse
import genanki

parser = argparse.ArgumentParser( description="Генерирует коллекцию Anki для вопросов")
parser.add_argument("-r", "--root", default=".", type=str, help="Путь к корню репозитория")
parser.add_argument("-c", "--category", default="A_B", type=str, help="Категория (A_B или C_D)")
parser.add_argument("-o", "--output", default="deck.apkg", type=str, help="Файл для колоды")

args = parser.parse_args()

topics_dir = os.path.join(args.root, "questions/"+args.category+"/topics")
topics_files = [f for f in os.listdir(topics_dir)]

extracted_questions = []

for file in topics_files:
    with open(os.path.join(topics_dir, file)) as json_data:
        questions = json.load(json_data)
        for question in questions:
            data = {
                "id": question["id"],
                "image": question["image"],
                "question": question["question"],
                "answer_variants": [variant["answer_text"] for variant in question["answers"]],
                "answer": question["correct_answer"],
                "answer_description": question["answer_tip"],
            }
            extracted_questions.append(data)



deck = genanki.Deck(
    2059400110,  # TODO: generate randomly
    'Вопросы ПДД ' + args.category,
)

media_files = []

model = genanki.Model(
    1607392319,  # TODO: generate randomly
    'Вопросы ПДД',
    fields=[
        {'name': 'Image'},
        {'name': 'Question'},
        {'name': 'AnswerVariants'},
        {'name': 'Answer'},
        {'name': 'AnswerDescription'},
    ],
    templates=[
        {
            'name': 'Card Template',
            'qfmt': '''
                {{#Image}}{{Image}}{{/Image}}
                <h3>{{Question}}</h3>
                {{AnswerVariants}}
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr>
                <div id="answer-text"><b>{{Answer}}</b></div>
                <div id="answer-desc">{{AnswerDescription}}</div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            margin: 0 auto;
            padding: 80px 20px;
            max-width: 650px;
            text-align: left;
            line-height: 1.5;
            background-color: white;
        }
        img {
            margin: 0 auto;
        }
        ol {
            padding-left: 0;
            list-style: inside decimal;
        }
        li:not(:first-child) { 
            margin-top: 0.2em; 
        }
        #answer, #answer-desc {
            margin-top: 0.4em; 
        }
    '''
)

for question in extracted_questions:
    image_path = os.path.abspath(question['image'])
    image_name = os.path.basename(image_path)
    if os.path.exists(image_path) and 'no_image' not in image_path:
        media_files.append(image_path)  
    else:
        image_name = ""

    answer_variants_html = '<ol>' + ''.join(
        f'<li>{variant}</li>' for variant in question['answer_variants']
    ) + '</ol>'

    note = genanki.Note(
        model=model,
        fields=[
            f"<img src='{image_name}' />" if image_name else "",
            question['question'],
            answer_variants_html,
            question['answer'],
            question['answer_description']
        ]
    )
    deck.add_note(note)

package = genanki.Package(deck)
package.media_files = media_files

package.write_to_file(args.output)
