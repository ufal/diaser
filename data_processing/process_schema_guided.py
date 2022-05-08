import argparse
import glob
import os, sys
import json
from pprint import pprint
import random
from data_processing.annotation_schema import Dialogue, Utterance
from data_processing.merge_data import write_json
from data_processing.da import DAI
from data_processing.ontology_unifier import get_ontology_unifier
import data_processing.getInconsistency as ginc
from data_processing.build_sgd_db import check_value

OTGY = json.load(fp=open('data/mwoz_ontology.json'))


def add_inconsistencies(dial, ontology=json.load(fp=open('data/mwoz_ontology.json'))):
    origin = dial.get_origin()
    if origin == "dstc":
        dialogue = [turn['text'] for turn in dial._data['utterances']]
        
        new_dial, incs = ginc.errors(dialogue, ontology, 0)
        for i, turn in enumerate(dial._data['utterances']):
            dial._data['utterances'][i]["inconsistency"] = incs[i]
            dial._data['utterances'][i]["annotation_fixes"] = []
            sys.exit()


def add_annotation_errors(dial, mwoz21, mwoz23, mwoz24):
    origin = dial.get_origin()
    if origin == "multiwoz":
        ginc.get_annotation_mwoz(dial, mwoz21, mwoz23, mwoz24)


def load_split(data_dir, ontology_unifier, original_dataset):
    data = []
    for fn in glob.glob(f'{data_dir}/*json'):
        data.extend(load_file(fn,
                              ontology_unifier,
                              original_dataset,
                              # delexicalize for schema using frames
                              # for mw, delexicalization is done later using DAs
                              do_delex=(original_dataset == 'schema')))
    return data


def load_camrest_ontology(db_file, otgy_file):
    ontology = {}
    if db_file is not None:
        with open(db_file, 'rt') as f:
            db = json.load(f)
            for entity in db:
                for key, val in entity.items():
                    ontology[val] = key
    if otgy_file is not None:
        with open(otgy_file, 'rt') as f:
            otgy = json.load(f)
            for val in otgy:
                ontology[val] = key
    return ontology


def load_filedstc(fn, ontology_unifier, camrest_ontology):
    with open(fn, 'rt') as fd:
        data = json.load(fd)
    loaded = []
    for dial in data:
        state_dic = []
        utterances = []
        slots = []
        values = []
        elems = 0
        previous = ""
        for n, turn in enumerate(dial['dial']):
            
            utt = ""
            nlu = dict()
            
            for key in turn:
                if key == 'usr':
                    if turn['usr']['slu'] == []:
                        intent = ""
                    
                    else:
                        
                        intent = turn['usr']['slu'][0]['act']
                        original = turn[key]['slu']
                        for i in range(len(original)):
                            for j in range(len(original[i]['slots'])):
                                if original[i]['slots'][j][0] == 'slot':
                                    turn[key]['slu'][i]['slots'][j][0] = turn[key]['slu'][i]['slots'][j][1]
                                    turn[key]['slu'][i]['slots'][j][1] = ""
                        
                        nlu.update({elem[0]: (act['act'], elem[1]) for act in original for elem in act['slots']})
                        for act in original:
                            for elem in act["slots"]:
                                state_dic.append((elem[0], elem[1]))
                    
                    for elem in state_dic:
                        if elem[0] not in slots:
                            slots.append(elem[0])
                            values.append(elem[1])
                        else:
                            values[slots.index(elem[0])] = elem[1]
                    utt = Utterance(
                        actor='user',
                        turn=int(turn['turn']),
                        utterance=turn['usr']['transcript'],
                        nlu=[DAI(val[0], ontology_unifier.map_slot(slot), val[1]) for slot, val in nlu.items()],
                        intent=intent,
                        state={f'restaurant-{slots[i]}': values[i] for i in range(len(slots)) if slots[i] != 'this'}
                    )
                    utterances.append(utt)
                elif key == 'sys':
                    if turn['sys']['DA'] == []:
                        intent = ""
                    
                    else:
                        original = turn[key]['DA']
                        for i in range(len(original)):
                            for j in range(len(original[i]['slots'])):
                                if original[i]['slots'][j][0] == 'slot':
                                    turn[key]['DA'][i]['slots'][j][0] = turn[key]['DA'][i]['slots'][j][1]
                                    turn[key]['DA'][i]['slots'][j][1] = ""
                    
                    intent = turn['sys']['DA'][0]['act']
                    original = turn[key]['DA']
                    nlu.update(
                        {elem[0]: (act['act'], elem[1]) for act in original for elem in act['slots'] if act['act']})
                    try:
                        for act in original:
                            if type(act['slots'][0]) == str:
                                
                                state_dic.append((act['slots'][0], ''))
                            elif len(act['slots'][0]) > 1:
                                for sl in act['slots']:
                                    state_dic.append((sl[0], sl[1]))
                    except IndexError:
                        pass
                    
                    for elem in state_dic:
                        if elem[0] not in slots:
                            slots.append(elem[0])
                            values.append(elem[1])
                        else:
                            values[slots.index(elem[0])] = elem[1]
                    
                    utt = Utterance(
                        actor='system',
                        turn=int(turn['turn']),
                        utterance=turn[key]['sent'],
                        nlu=[DAI(val[0], ontology_unifier.map_slot(slot), val[1]) for slot, val in nlu.items()],
                        intent=intent,
                        state={f'restaurant-{slots[i]}': values[i] for i in range(len(slots)) if slots[i] != 'this'},
                        delexicalize=True,
                        delex_ontology=camrest_ontology,
                    )
                    
                    utterances.append(utt)
        for i in range(len(dial['goal']['constraints'])):
            for j in range(len(dial['goal']['constraints'][i])):
                dial['goal']['constraints'][j][0] = ontology_unifier.map_slot(dial['goal']['constraints'][j][0])
        for i in range(len(dial['goal']['request-slots'])):
            dial['goal']['request-slots'][i] = ontology_unifier.map_slot(dial['goal']['request-slots'][i])
        dial['goal'] = {"restaurant": dial['goal']}
        dial_obj = Dialogue(
            dialogue_id=dial['dialogue_id'],
            domains=["restaurant"],
            utterances=utterances,
            goal=dial['goal'],
            original_dataset=dial['original_data'],
            split=dial['split'],
        )
        loaded.append(dial_obj.dump())
    # add_inconsistencies(dial_obj)
    # add_annotation_errors(dial_obj)
    return loaded


def preprocess_goal(dialog, ontology_unifier, origin, mwoz21):
    did = dialog['dialogue_id']
    dialog.update({"goal": {}})
    if origin == 'multiwoz':
        """
         "goal": {
      "constraints": [
        [
          "price_range",
          "expensive"
        ],
        [
          "location",
          "south"
        ]
      ],
      "request-slots": [
        "address"
      ],
      "text": "Task 11193: You are looking for an expensive restaurant and it should be in the south part of town. Make sure you get the address of the venue."
    },
        """
        # did = dialog['dialogue_id']
        # dialog.update({"goal": {}})
        # pprint(dialog)
        
        dial21 = mwoz21[did]
        goal = dial21['goal']
        # pprint(dial21['goal'])
        for domain in goal:
            if domain == "message":
                dialog["goal"].update({"text": '. '.join(
                    [elem.replace("<span class='emphasis'>", "").replace('</span>', '') for elem in goal[domain]])})
            elif domain == 'topic':
                pass
            else:
                if goal[domain]:
                    if domain not in dialog['goal']:
                        dialog['goal'][domain] = {"constraints": [], "request-slots": [], "book": []}
                        for elem in goal[domain]['info']:
                            dialog['goal'][domain]["constraints"].append([elem, goal[domain]['info'][elem]])
                        if "reqt" in goal[domain]:
                            for elem in goal[domain]['reqt']:
                                dialog['goal'][domain]["request-slots"].append(elem)
                        if "book" in goal[domain]:
                            for elem in goal[domain]['book']:
                                dialog['goal'][domain]["book"].append(elem)
    
    elif origin == "schema":
        
        turns = dialog['turns']
        for turn in turns:
            
            if turn['speaker'] == 'USER':
                for elem in turn['frames']:
                    actions = elem['actions']
                    domain = ontology_unifier.map_domain(elem['service'])
                    if domain not in dialog['goal']:
                        dialog['goal'][domain] = {}
                    for action in actions:
                        if action['act'] == "INFORM":
                            slot = action['slot']
                            value = action['values']
                            value = value[0]
                            if slot == 'intent' or not slot:
                                continue
                            if "constraints" not in dialog['goal'][domain]:
                                dialog['goal'][domain]["constraints"] = [[slot, value]]
                            updated = False
                            for n, elem in enumerate(dialog['goal'][domain]["constraints"]):
                                
                                if elem[0] == slot:
                                    dialog['goal'][domain]["constraints"][n][1] = value
                                    updated = True
                                    break
                            if not updated:
                                dialog['goal'][domain]["constraints"].append([slot, value])
                        
                        elif action['act'] == "REQUEST":
                            slot = action['slot']
                            if slot == 'intent' or not slot:
                                continue
                            if "request-slots" not in dialog['goal'][domain]:
                                dialog['goal'][domain]["request-slots"] = []
                            dialog['goal'][domain]["request-slots"].append(slot)


def load_file(fn, ontology_unifier, original_dataset, do_delex=False):
    subcat = ['football',"baseball","soccer","pop","electronica","rock","country"]
    with open(fn, 'rt') as fd:
        data = json.load(fd)
    # mwoz21 = json.load(open('../../multiwoz/data/MULTIWOZ2.1/data.json'))
    # mwoz23 = json.load(open('../../multiwoz/data/MULTIWOZ2.3/data.json'))
    # mwoz24 = json.load(open('../../multiwoz/data/MULTIWOZ2.4/data.json'))
    fn = fn.replace('\\','/')
    split = fn.split("/")[-2]
    if split not in ['train', 'dev', 'test']:
        raise ValueError(f'split {split} unknown')
    loaded = []
    for dial in data:
        if 'turns' not in dial:
            continue
        # print(dial)
        # preprocess_goal(dial, ontology_unifier, original_dataset, mwoz21)
        domains = [ontology_unifier.map_domain(service) for service in dial['services']]
        utterances = []
        previous = ""
        for n, turn in enumerate(dial['turns']):
            state_dict = dict()
            nlu = dict()
            substitutions = []
            intents = list(set([frame['state']['active_intent'] for frame in turn['frames'] if
                                'state' in frame and frame['state']['active_intent'] != 'NONE']))
            for frame in turn['frames']:
                if 'slots' in frame:
                    for slot in frame['slots']:
                        if "start" not in slot:
                            continue
                        start = slot["start"]
                        end = slot["exclusive_end"]
                        if start != end:
                            key = ontology_unifier.map_slot(slot["slot"], original_dataset)
                            substitutions.append((start, end, key))
                
                if 'state' in frame:
                    state = frame['state']
                    service =  ontology_unifier.map_domain(frame['service'])
                    
                    intents = [ontology_unifier.map_intent(i, service) for i in intents]
                    if len(intents) == 0:
                        intent = service
                    else:
                        intent = ','.join(intents)
                    tobechanged = {}
                    for sl, val in state['slot_values'].items():
                        old = sl

                        if "calendar" in intent :
                            sl = sl.replace('event_',"").replace("event-","")
                            if "calendar" not in sl :
                                sl = "calendar-" +sl
                                if "location" in sl :
                                    sl = sl.replace('location',"area")
                        if "restaurant" in intent and sl =="day":
                            sl = sl.replace('day',"book_day")
                        if "city" in sl  and intent == "service":
                            sl = "area"
                        if sl == "location" or sl == "area":
                            if "service" not in intent:

                                sl = "city"
                            else:
                                sl = "area"

                        if '-' in sl:
                            if ontology_unifier.is_domain(sl.split('-')[0]) :
                                sl = sl.split('-')[0] + '-' + ontology_unifier.map_slot(sl.split('-')[1])
                            else :
                                sl = intent+'-' +ontology_unifier.map_slot(sl)
                        elif '_' in sl :
                            if ontology_unifier.is_domain(sl.split('_')[0]):

                                sl = sl.split('_')[0] + '-' + ontology_unifier.map_slot(sl.split('_')[1])
                            else :
                                sl = intent + '-' + ontology_unifier.map_slot(sl)
                        else :
                            sl = intent+'-'+ontology_unifier.map_slot(sl)
                        old_v = val
                        val = val[0]
                        if val.endswith(' '):
                            val = val[:-1]
                        if val.startswith(' '):
                            val = val[1:]
                        val = val.replace(' ','_')
                        val = val.lower()
                        state_dict[sl] = val
                        if "time" in sl :
                            previous = val
                        if sl != old :
                            tobechanged.update({sl:old})
                        else :
                            state['slot_values'][sl] = val
                    for elem,old in tobechanged.items() :
                        state["slot_values"][elem] = state["slot_values"].pop(old)
                nlu.update({act['slot']: (act['act'].lower(), ' '.join(act['values'])) for act in frame['actions']})
                
            substitutions.sort(key=lambda x: x[0], reverse=True)
            delex_text = turn['utterance']
            if do_delex:
                for s, e, k in substitutions:
                    delex_text = f'{delex_text[:s]}[{k}]{delex_text[e:]}'
            utt = Utterance(
                actor=turn['speaker'],
                turn=n // 2 + 1,
                utterance=turn['utterance'],
                delex_utterance=delex_text,
                nlu=[DAI(val[0], ontology_unifier.map_slot(slot), val[1]) for slot, val in nlu.items()],
                intent=intent,
                state=state_dict
            )
            utterances.append(utt)
        dial_obj = Dialogue(
            dialogue_id=dial['dialogue_id'],
            domains=domains,
            utterances=utterances,
            goal="",
            original_dataset=original_dataset,
            split=split,
        )
        # add_inconsistencies(dial_obj)
        # add_annotation_errors(dial_obj,mwoz21,mwoz23,mwoz24)
        loaded.append(dial_obj.dump())
    return loaded


def main(args):
    if args.dataset == 'dstcamrest':
        ontology_unifier = get_ontology_unifier('dstcamrest')
        camrest_ontology = load_camrest_ontology(args.db, args.otgy)
        data = load_filedstc(os.path.join(args.data_dir, 'dstccamrest.json'), ontology_unifier, camrest_ontology)
        write_json(args.output_file, data, compress=False)
    elif args.dataset == "multiwoz":
        ontology_unifier = get_ontology_unifier('multiwoz')
        data = load_split(os.path.join(args.data_dir, args.split), ontology_unifier, args.dataset)
        write_json(args.output_file, data, compress=args.compress)
    else:
        ontology_unifier = get_ontology_unifier('schema')
        data = load_split(os.path.join(args.data_dir, args.split), ontology_unifier, args.dataset)
        write_json(args.output_file, data, compress=args.compress)
        # data = load_split(os.path.join('../../sgd/', 'dev'), ontology_unifier, 'schema')
        # write_json(args.output_file, data, compress=args.compress)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir')
    parser.add_argument('--dataset', choices=['multiwoz', 'schema', 'dstcamrest'], required=True)
    parser.add_argument('--split', default='train')
    parser.add_argument('--output_file')
    parser.add_argument('--db')
    parser.add_argument('--otgy')
    parser.add_argument('--compress', action='store_true')
    args = parser.parse_args()
    main(args)
