import argparse
import json
import os
import sys
from glob import glob


def parse_camrest(jsfile):
    camrest = json.load(open(jsfile))
    for i in range(len(camrest)):
        camrest[i].update({'original_data': 'camrest'})
        camrest[i].update({'split':'traindev'})
        camrest[i]['dialogue_id'] = 'CR' + str(i)
        for j in range(len(camrest[i]['dial'])):
            camrest[i]['dial'][j]['turn'] += 1
            if camrest[i]['dial'][j]['sys']['DA'] == []:
                camrest[i]['dial'][j]['sys']['DA'] = [{'act': '', 'slots': []}]
            else:
                camrest[i]['dial'][j]['sys']['DA'] = [{'act': '', 'slots': camrest[i]['dial'][j]['sys']['DA']}]

    return camrest


def convert_dstc_to_camrest(label, log):
    jlabel = json.load(open(label))
    jlog = json.load(open(log))

    dic = {}
    if 'test' in label :
    	dic['split'] = 'test'
    else :
    	dic['split'] = 'traindev'
    id = jlabel['session-id']
    assert id == jlog['session-id']
    dic['dialogue_id'] = id
    dic['finished'] = jlabel['task-information']['feedback']['success']
    dic['goal'] = jlabel['task-information']['goal']
    dic['dial'] = []
    dic['original_data'] = 'dstc2'
    for i in range(len(jlabel['turns'])):
        turn_u = jlabel['turns'][i]
        turn_s = jlog['turns'][i]
        dic['dial'].append([])
        dic['dial'][i] = {'turn': i + 1}
        dic['dial'][i].update(
            {'system': {'sent': turn_s['output']['transcript'], 'DA': turn_s['output']['dialog-acts']}}
        )
        dic['dial'][i].update({'user': {'transcript': turn_u['transcription'], 'slu': turn_u['semantics']['json']}})
        # Fix naming
        dic['dial'][i]['sys'] = dic['dial'][i].pop('system')
        dic['dial'][i]['usr'] = dic['dial'][i].pop('user')

    return dic


def recursive_pair(datafile, pairs=[]):
    for elem in datafile:
        pairs.append([e.replace('\\','/') for e in glob(elem + '/*')])
    return pairs



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--camrest-path',
        default='../source_diaser_data/CamRest676/CamRest676.json'
    )
    parser.add_argument(
        '--dstc-dir',
        default='../source_diaser_data/dstc2'
    )
    parser.add_argument('--output-file')
    args = parser.parse_args()
    print(args)

    camrest = parse_camrest(args.camrest_path)
    pairs = recursive_pair(glob(f'{args.dstc_dir}/**/**/*'))
    liste = []
    for pair in pairs:
        label_path = [x for x in pair if 'label' in x][0]
        log_path = [x for x in pair if 'log' in x][0]
        dic = convert_dstc_to_camrest(label_path, log_path)
        liste.append(dic)

    camrest += liste
    os.makedirs(
        os.path.join(*args.output_file.split('/')[:-1]),
        exist_ok=True,
    )
    out = open(args.output_file, 'w')
    out.write(json.dumps(camrest, indent=4))
