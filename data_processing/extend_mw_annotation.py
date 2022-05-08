import argparse
from data_processing.merge_data import read_json, write_json
from data_processing.annotation_schema import Dialogue


def main(args):
    data = read_json(args.input_file, compressed=args.input_file.endswith('zip'))
    acts_dict = read_json(args.das_file, compressed=args.das_file.endswith('zip'))
    goal_data = read_json(args.goal_file)
    processed_data = []
    for dial in data:
        dial = Dialogue.load(dial)
        if dial['dialogue_id'] in goal_data:
            dial.extend_goal(goal_data[dial['dialogue_id']]['goal'])
        if dial['dialogue_id'] not in acts_dict:
            processed_data.append(dial.dump())
            continue
        acts = acts_dict[dial['dialogue_id']]
        dial.extend_user_acts(acts)
        processed_data.append(dial.dump())
    write_json(args.output_file, processed_data, compress=args.compress)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file')
    parser.add_argument('--das_file')
    parser.add_argument('--goal_file')
    parser.add_argument('--output_file')
    parser.add_argument('--compress', action='store_true')
    args = parser.parse_args()

    main(args)
