from glob import glob
import json
import sys, time
from pprint import pprint
import copy
import data_processing.ontology_unifier as ontology_unif

TAB = "\t"

# inf = open("../data/dialog-bAbI-tasks/artarin.txt")
# out = open("artarin2.txt", 'w')
# i = 0
# for line in inf.readlines():
#     i += 1
#     line = str(i)+" "+" ".join(line.split(" ")[1:])
#     out.write(line)
domainz = ["restaurant", "hotel", "attraction", "train", "taxi", "hospital", "police", "bus"]

intentz = ["booking", "general", "inform", "request", "recommend", "book", "select", "sorry"]

requestable = ["address", "postcode", "phone", "time", "reference", "parking", "stars", "internet", "day",

               "arriveby", "departure",

               "destination", "leaveat", "duration", "trainid", "department", "stay", "id", "ticket", "openhours"]

informable = ["none", "pricerange", "type", "food", "name", "area", "choice", "people", "price", ]

mapping = {"addr": "address", "depart": "departure", "leave": "leaveat", "arrive": "arriveby", "fee": "price",
           "dest": "destination", "ref": "reference", "car": "type", "post": "postcode", "open": "openhours"}


def get_generic(slot):
    if slot in mapping:
        return mapping[slot]
    else:
        return slot


def fill_elem(d, intt, inf, rek, d22, d23):
    for da in d22:
        domain, intent = da.lower().split('-')
        if da not in d23:
            d.append(domain)
            intt.append(intent)
        else:
            for elem in d22[da]:
                slot, value = elem
                slot = slot.lower()
                slot = get_generic(slot)
                if elem not in d23[da]:
                    if slot in informable:
                        inf.append(slot)
                    elif slot in requestable:
                        rek.append(slot)
                    else:
                        raise ValueError(f'slot {slot} doesnt belong to any category')


def dict_to_lists(dict22, dict23, text):
    domains = []
    intents = []
    inform = []
    request = []
    if dict23 == dict22:
        return [], [], [], []
    elif dict23 == 'No Annotation':
        return [], [], [], []
    else:
        fill_elem(domains, intents, inform, request, dict23, dict22)
        fill_elem(domains, intents, inform, request, dict22, dict23)

        return list(set(domains)), list(set(intents)), list(set(inform)), list(set(request))


def analyze_dict(inf_dic, dial, turn, dom, inte, inf, req, total, domis, intmis, infmis, reqmis, totalmis):
    # for turn in dialog
    file_name = dial['dialogue_id']  # dialogue ID
    # print(f'act = {act}')
    # for cle in act[0] :
    #     for word in cle.split('-') :
    #         if

    total_inf, domain_inf, intent_inf, infor_inf, req_inf = 0, 0, 0, 0, 0

    # difference between expected and predicted DA length

    # print(f"total inf = {total_inf}")

    def fill_dic(total, dic, tur, file, refname):
        if total not in dic[refname]:
            dic[refname][total] = {tur: [file]}
        else:

            if tur not in dic[refname][total]:
                dic[refname][total][tur] = [file]
            else:
                dic[refname][total][tur].append(file)
        # print(dic)

    total_inf = len(total) - len(totalmis)
    fill_dic(total_inf, inf_dic, turn, file_name, 'total_diff')

    domain_inf = len(dom) - len(domis)
    # print(domain_inf)
    fill_dic(domain_inf, inf_dic, turn, file_name, 'domain_diff')
    intent_inf = len(inte) - len(intmis)
    # print(intent_inf)
    fill_dic(intent_inf, inf_dic, turn, file_name, 'intent_diff')
    infor_inf = len(inf) - len(infmis)
    # print(infor_inf)
    fill_dic(infor_inf, inf_dic, turn, file_name, 'infor_diff')
    req_inf = len(req) - len(reqmis)
    # print(req_inf)
    fill_dic(req_inf, inf_dic, turn, file_name, 'req_diff')

    # print(total_inf)
    # pprint(inf_dic)
    # sys.exit()

    def correct_info(reflist, errlist, toomuchlist, tur, file, refname, dic):
        """
        get diffs between expected and predicted for each kind of domain/intent/inform/request
        reflist = list of possible elements of each information type : for domain, list = [restaurant,hotel..]
        explist = list of missing elements
        predist = list of toomuch
        tur = current turn number
        file = dialogue id
        refname = name of the general dict's key (domain,intent...)
        dic = big nested dict containing the whole structure
        """

        for elem in reflist:

            if elem in errlist:
                if elem not in dic[refname]:
                    dic[refname][elem]: {tur: [file], "missing": 1}
                else:
                    if "missing" not in dic[refname][elem]:
                        dic[refname][elem]['missing'] = 1
                    else:
                        dic[refname][elem]['missing'] += 1
                    if tur not in dic[refname][elem]:
                        dic[refname][elem][tur] = [file]
                    else:
                        dic[refname][elem][tur].append(file)
            else:
                if elem in toomuchlist:
                    if elem not in dic[refname]:
                        dic[refname][elem] = {tur: [file], "toomuch": 1}
                    else:
                        if "toomuch" not in dic[refname][elem]:
                            dic[refname][elem]['toomuch'] = 1
                        else:
                            dic[refname][elem]['toomuch'] += 1
                        if tur not in dic[refname][elem]:
                            dic[refname][elem][tur] = [file]
                        else:
                            dic[refname][elem][tur].append(file)

    correct_info(domainz, domis, dom, turn, file_name, "domain", inf_dic)
    correct_info(intentz, intmis, inte, turn, file_name, "intent", inf_dic)
    correct_info(informable, infmis, inf, turn, file_name, "informable", inf_dic)
    correct_info(requestable, reqmis, req, turn, file_name, "requestable", inf_dic)


def get_mwoz_diffs(mwoz22, mwoz23, mwoz24, diaser, shortall, shortmwoz, shortmwozdom, shortmwozint,
                   shortmwozinf, shortmwozreq, shortmwozdomint, shortmwozdominf, shortmwozdomreq, shortmwozintinf,
                   shortmwozintreq, shortmwozinfreq, shortmwozdomintinf, shortmwozdomintreq, shortmwozdominfreq,
                   shortmwozintinfreq,
                   errs, total, empty):
    jmwoz22 = json.load(open(mwoz22))

    #  , inte, inf, reqs, domint,
    #                                             dominf, domreq, intinf, intreq, infreq, domintinf, domintreq, dominfreq,
    #                                             intinfreq
    jmwoz23 = json.load(open(mwoz23))
    jmwoz24 = json.load(open(mwoz24))
    diasersson = json.load(open(diaser))
    h = 0
    k = 0
    inf_dic = {"total_diff": {}, "domain_diff": {}, "intent_diff": {}, "infor_diff": {}, "req_diff": {}, "domain": {},
               "intent": {}, "informable": {}, "requestable": {}}
    keyerr = 0
    for h, dial in enumerate(diasersson):
        did = dial["dialogue_id"]
        splitt = dial['split']
        try:
            k += 1
            da22 = jmwoz22[did]['log']
            current_dial = copy.deepcopy(jmwoz22[did])
            shortmwoz.update({did: copy.deepcopy(current_dial)})
            shortmwozdom.update({did: copy.deepcopy(current_dial)})
            shortmwozint.update({did: copy.deepcopy(current_dial)})
            shortmwozinf.update({did: copy.deepcopy(current_dial)})
            shortmwozreq.update({did: copy.deepcopy(current_dial)})
            shortmwozdomint.update({did: copy.deepcopy(current_dial)})
            shortmwozdominf.update({did: copy.deepcopy(current_dial)})
            shortmwozdomreq.update({did: copy.deepcopy(current_dial)})
            shortmwozintinf.update({did: copy.deepcopy(current_dial)})
            shortmwozintreq.update({did: copy.deepcopy(current_dial)})
            shortmwozinfreq.update({did: copy.deepcopy(current_dial)})
            shortmwozdomintinf.update({did: copy.deepcopy(current_dial)})
            shortmwozdomintreq.update({did: copy.deepcopy(current_dial)})
            shortmwozdominfreq.update({did: copy.deepcopy(current_dial)})
            shortmwozintinfreq.update({did: copy.deepcopy(current_dial)})
            shortall.update({did: copy.deepcopy(current_dial)})
            total += 1
        except KeyError:
            keyerr += 1
            continue
        if dial["split"] == 'train':
            da23 = jmwoz23[did]['log']
        else:
            da23 = jmwoz24[did]['log']
        to_remove = 0
        # print('\n'.join([d['text']for d in da22]))
        # # print(len(da22))
        # print(len(diasersson[h]['utterances']))
        # print('\n'.join([d['utterance']for d in diasersson[h]['utterances']]))
        for i in range(0, len(da22), 2):
            try:
                turn22 = da22[i]['dialog_act']
                turn22sys = da22[i + 1]['dialog_act']
            except KeyError:
                turn22 = []
            try:
                turn23 = da23[i]['dialog_act']
                turn23sys = da23[i + 1]['dialog_act']
            except KeyError:
                turn23 = []

            dom_sup = []
            inte_sup = []
            inf_sup = []
            req_sup = []

            dom_mis = []
            inte_mis = []
            inf_mis = []
            req_mis = []
            fill_elem(dom_mis, inte_mis, inf_mis, req_mis, turn22, turn23)
            fill_elem(dom_mis, inte_mis, inf_mis, req_mis, turn22sys, turn23sys)
            fill_elem(dom_mis, inte_mis, inf_mis, req_mis, turn22, turn23)
            fill_elem(dom_mis, inte_mis, inf_mis, req_mis, turn22sys, turn23sys)
            total_sup = list(set(dom_sup + inte_sup + inf_sup + req_sup))
            total_mis = list(set(dom_mis + inte_mis + inf_mis + req_mis))
            analyze_dict(inf_dic, dial, i / 2 + 1, dom_sup, inte_sup, inf_sup, req_sup, total_sup, dom_mis, inte_mis,
                         inf_mis, req_mis, total_mis)
            # print(threshold) 5 : errs = 10461, total = 10437, empty = 0
            # if threshold > 5:
            errs += 1

            def removing(file, ind, to_remov, removed, dialid=did):
                # assert ind < len(file[dialid]['log'])
                user = file[dialid]['log'][ind - to_remov]
                system = file[dialid]['log'][ind + 1 - to_remov]
                # print(f'lines {user} and {system} will be removed')
                file[dialid]['log'].remove(system)
                file[dialid]['log'].remove(user)
                if not removed:
                    to_remov += 2
                removed = True
                return removed, to_remov

            err = ""
        #     if dom or dom2:
        #         removed,to_remove = removing(shortmwozdom, i, to_remove, removed)
        #         removed,to_remove = removing(shortmwoz, i, to_remove, removed)
        #         if inte or inte2:
        #
        #             removed,to_remove = removing(shortmwozdomint, i, to_remove, removed)
        #             if inf or inf2:
        #                 removed,to_remove = removing(shortmwozdomintinf, i, to_remove, removed)
        #                 if req or req2:
        #                     removed,to_remove = removing(shortall, i, to_remove, removed)
        #             else:
        #                 if req or req2:
        #                     removed,to_remove = removing(shortmwozdomintreq, i, to_remove, removed)
        #
        #         elif inf or inf2:
        #             removed,to_remove = removing(shortmwozdominf, i, to_remove, removed)
        #             if req or req2:
        #                 removed,to_remove = removing(shortmwozdominfreq, i, to_remove, removed)
        #         else:
        #             if req or req2:
        #                 removed,to_remove = removing(shortmwozdomreq, i, to_remove, removed)
        #         err += "+".join(["domain" for elem in dom])
        #     elif inte or inte2:
        #         if not removed:
        #             removed,to_remove = removing(shortmwoz, i, to_remove, removed)
        #
        #         removed,to_remove = removing(shortmwozint, i, to_remove, removed)
        #         if inf or inf2:
        #             removed,to_remove = removing(shortmwozintinf, i, to_remove, removed)
        #             if req or req2:
        #                 removed,to_remove = removing(shortmwozintinfreq, i, to_remove, removed)
        #         else:
        #             if req or req2:
        #                 removed,to_remove = removing(shortmwozintreq, i, to_remove, removed)
        #
        #         if not err:
        #             err += "+".join(["intent" for elem in inte])
        #         else:
        #             err += "+" + "+".join(["intent" for elem in inte])
        #
        #     elif inf or inf2:
        #         if not removed:
        #             removed,to_remove = removing(shortmwoz, i, to_remove, removed)
        #         removed,to_remove = removing(shortmwozinf, i, to_remove, removed)
        #         if req or req2:
        #             removed,to_remove = removing(shortmwozinfreq, i, to_remove, removed)
        #
        #         if not err:
        #             err += "+".join(["intent" for elem in inf])
        #         else:
        #             err += "+" + "+".join(["intent" for elem in inf])
        #
        #     elif req or req2:
        #         if not removed:
        #             removed,to_remove = removing(shortmwoz, i, to_remove, removed)
        #         removed,to_remove = removing(shortmwozreq, i, to_remove, removed)
        #         if not err:
        #             err += "+".join(["intent" for elem in req])
        #         else:
        #             err += "+" + "+".join(["intent" for elem in req])
        #     if not err:
        #         err = None
        #     if i % 2 != 0:
        #         # print(i)
        #         # print(len(diasersson[h]["utterances"]))
        #         diasersson[h]['utterances'][i]['inconsistency'] = err
        # if not shortmwoz[did]['log']:
        #     empty += 1
        # print('\n'.join([d['text']for d in shortmwoz['log']]))
        # sys.exit()
    json.dump(inf_dic, fp=open('../../consistency/script/analyze_dict.json', 'w'), indent=4)
    # return empty, errs, total


def get_annotation_mwoz(dial, mwoz22, mwoz23, mwoz24):
    jmwoz22 = mwoz22
    jmwoz23 = mwoz23
    jmwoz24 = mwoz24
    unifyer = ontology_unif.get_ontology_unifier("schema")
    h = 0
    k = 0
    keyerr = 0
    did = dial._data["dialogue_id"]
    splitt = dial._data['split']
    try:
        k += 1
        da22 = jmwoz22[did]['log']
        current_dial = copy.deepcopy(jmwoz22[did])
    except KeyError:
        keyerr += 1
    if splitt == 'train':
        da23 = jmwoz23[did]['log']
    else:
        da23 = jmwoz23[did]['log']
    to_remove = 0
    for i in range(len(da22)):
        try:
            turn22 = da22[i]['dialog_act']
        except KeyError:
            turn22 = []
        try:
            turn23 = da23[i]['dialog_act']
        except KeyError:
            turn23 = []
        print(turn22)
        fixed = {"missing": [], "superfluous": []}

        for key in turn22:
            print(key)
            if key not in turn23:
                for elem in turn22[key]:

                    if len(elem) == 1:
                        elem.append('?')
                    elem[0] = unifyer.map_slot(elem[0])
                    fixed["superfluous"].append(key.lower() + "(" + elem[0] + "=" + elem[1] + ")")
            else:
                for elem in turn22[key]:
                    if elem not in turn23[key]:
                        if len(elem) == 1:
                            elem.append('?')
                        print(elem[0])
                        elem[0] = unifyer.map_slot(elem[0])
                        print(elem[0])
                        fixed["superflous"].append(key.lower() + "(" + elem[0] + "=" + elem[1] + ")")
        for key in turn23:
            if key not in turn22:
                for elem in turn23[key]:

                    if len(elem) == 1:
                        elem.append('?')
                    elem[0] = unifyer.map_slot(elem[0])
                    print(elem[0])
                    fixed["missing"].append(key.lower() + "(" + elem[0] + "=" + elem[1] + ")")
            else:
                for elem in turn23[key]:
                    if elem not in turn22[key]:
                        print(elem)
                        print(elem[0])
                        if len(elem) == 1:
                            elem.append('?')
                        elem[0] = unifyer.map_slot(elem[0])
                        print(elem[0])
                        fixed["missing"].append(key.lower() + "(" + elem[0] + "=" + elem[1] + ")")

        print(fixed)
        sys.exit()


def get_polarity(diaser, dscr, ontology):
    diasersson = json.load(diaser)
    dscrsson = json.load(dscr)
    for i in range(len(dscrsson)):
        # if "voip" in dscrsson[i]['dialogue_id']:
        did = dscrsson[i]['dialogue_id']
        for j in range(len(diasersson)):
            if diasersson[j]["dialogue_id"] == did:
                diasersson[j]['success'] = dscrsson[i]['finished']
                babied = []
                count = 0
                for k in range(0, len(diasersson[j]["utterances"]), 2):
                    count = k / 2
                    babied.append(f"{int(count)}\
                     {diasersson[j]['utterances'][k]['utterance']}{TAB}{diasersson[j]['utterances'][k + 1]['utterance']}")
                # babies = "\n".join(babied)

                new, error = errors(babied, ontology, 0)

                count = 1
                for trn in new:
                    try:
                        diasersson[j]["utterances"][count]['inconsistency'] = trn.split('(')[1].split(')')[0]
                    except IndexError:
                        diasersson[j]["utterances"][count]['inconsistency'] = None
                    count += 2
                pprint(diasersson[j])
                sys.exit()


def is_request(word, ontology):
    if word in ontology['requestable']:
        return True, word
    else:
        return False, 'nope'


def has_word(word, ontology):
    lonto = []
    for elem in ontology['informable']['food']:
        lonto.append(elem)
    for elem in ontology['informable']['area']:
        lonto.append(elem)
    for elem in ontology['informable']['pricerange']:
        if elem == "moderately":
            elem = "moderate"
        lonto.append(elem)
    if word in lonto:
        return True
    else:
        return False


def negation(word, ontology):
    if word in ontology['informable']["negation"]:
        return True
    else:
        return False


def errors(dialogue, ontology, errors):
    apied = False  # pas encore appel api
    entities = []
    repeatedUser = {}
    repeatedSystem = {}
    turns = 0
    new = []
    reason = []
    reasons = []
    for line in dialogue:
        if "<SILENCE>" in line:  # si l'utilisateur ne dit rien on est "gentil" avec le systeme
            new.append(line + '\n')
            inc = False
            continue

        if turns > 7:  # + de 7 tours de parole y a toujours un truc qui déconne
            inc = True
            errors += 1
        inc = False  # par défaut pas d'incohérence
        line = line.rstrip()
        if 'api_call no result' in line or 'sorry' in line:
            apied = False
            entities = [elem for elem in entities if elem not in ontology['informable'][
                'food']]  # on garde les entités non liées à la bouffe (souvent ce que le user change dans ses requetes)
        if '\t' in line:

            turns += 1
            user = line.split('\t')[0].split(' ')[1:]
            user = " ".join(user)
            system = line.split('\t')[1]
            if user not in repeatedUser:
                repeatedUser[user] = [1, apied]
            else:  # si le user dit au moins 2x la même chose ERREUR
                if repeatedUser[user][1] == apied:
                    repeatedUser[user][0] += 1
                    reason.append("intent")
                    inc = True
                    errors += 1
            if system not in repeatedUser:
                repeatedSystem[system] = [1, apied]
            else:  # si le system dit au moins 2x la même chose ERREUR
                if repeatedSystem[system][1] == apied:
                    repeatedSystem[system][0] += 1
                    reason.append("intent")
                    inc = True
                    errors += 1
            if not apied:
                if "how about" in user or "and" in user:
                    entities = []
                for word in user.split():
                    if has_word(word, ontology):  # on rajoute les entités grace à l'ontologie
                        entities.append(word.replace(' ', '_'))
                        print(entities)
            if 'api_call' in line and "no result" not in line:
                if apied:
                    entities = []
                    inc = False
                else:
                    apied = True
                    errs = 0
                    for elem in entities:
                        if elem not in system.split():
                            errs += 1
                            if errs >= 2:  # si dans l'appel api au moins deux entités sont manquantes: ERREUR
                                # reason = "wrong api call"
                                errors += 1
                                inc = True

            for i in range((len(user.split()))):
                if negation(user.split()[i], ontology) and len(user.split()) > i + 1:
                    if has_word(user.split()[i + 1], ontology):  # si la négation est pas prise en compte : ERREUR
                        reason.append("negation")
                        inc = True
                        errors += 1

            if "bye" in user.split() or "goodbye" in user.split() or "thank" in user.split() or "thanks" in user.split():
                if "welcome" not in system.split():
                    reason.append("intent")  # si l'un ou l'autre dit au revoir mais pas l'autre ERREUR
                    inc = True
                    errors += 1
            if "welcome" in system.split():
                if not "bye" in user.split() and not "goodbye" in user.split() and not "thank" in user.split() and not "user" in system.split():
                    inc = True
                    reason.append("intent")  # si l'un ou l'autre dit au revoir mais pas l'autre ERREUR
                    errors += 1
            # if apied:
            for elem in user.split():
                if elem == "center":  # redressement moche
                    elem = 'centre'

                so, word = is_request(elem, ontology)
                if so:
                    print("so")
                    if word not in system:  # si le systeme ne prend pas en compte la requete usr ERREUR
                        if word == 'type' or word == 'cuisine':
                            if 'food' not in system:
                                reason.append("inform")
                                inc = True
                                errors += 1
                        # if word == "address"
            if "area" in user or 'where' in user or 'part of town' in user:  # redressement moche
                if "centre" not in system and 'north' not in system and 'south' not in system and 'east' not in system and 'west' not in system:
                    inc = True
                    reason = "not understood area"
                    errors += 1
            if ("phone" in system and "phone" not in user) or ("address" in system and "address" not in user) or (
                    "post" in system and "post" not in user):  # incomplétude ici.
                inc = True
                reason.append("request")
        # if "eraina is a nice restaurant in the centre of town serving european food" in line:
        #     print(reason)
        #     sys.exit()
        #     _
        if inc:
            reason = "+".join(reason)
            # if 'several' in reason:
            #
            #     if new[-1][-2] != ')' and '<SILENCE>' not in new[-1]:
            #         new[-1] = new[-1].replace('\n', '')
            #         new[-1] += ' (' + reason.replace(' ', '_') + ')\n'
            # else:
            # line += '(inc)'
            line += ' (' + reason.replace(' ', '_') + ')'
        line += '\n'
        new.append(line)
        reasons.append(reason)
    return new, reasons


def post_prod(file, out, ontology):
    out = open(out, 'w')
    i = 0
    for line in file:
        if '\t' in line:
            user = line.split('\t')[0]
            system = line.split('\t')[1]
            if ('phone' in user and 'phone' not in system) or ('address' in user and 'address' not in system):
                if '(' not in line:
                    line = line.rstrip()
                    line += ' (uncomprehension)\n'
                    # sys.exit()
            if 'Sorry' in system or 'sorry' in system:

                for elem in user.split(' '):
                    food = has_word(elem, ontology)
                    if food:
                        if elem not in system:
                            if '(' not in line:
                                i += 1
                                line = line.rstrip()
                                line += ' (wrong_food)\n'

        out.write(line)

    print(i)


def open_dstc_dial(file, pack='traindev'):
    utterances = []
    errors = {}
    success = None
    polarity = 0
    for line in file['turns']:

        if line["transcription"] != 'noise' and line['transcription'] != 'unintelligible' and line[
            'transcription'] != 'sil':
            utterances.append(
                line['transcription'].replace(" unintelligible", "").replace("noise", "").replace('  ', " "))
    rest = file['task-information']
    for elem in rest:
        if elem == 'feedback':

            if rest[elem]['success'] == True:
                success = True
            else:
                success = False
            diff = 0
            words = rest[elem]['questionnaire'][0][1].split()

            if 'slightly' in words:
                diff = 1
            elif 'strongly' in words:
                diff = 3
            else:
                diff = 2
            if 'agree' not in words:
                polarity = (- diff) + 2
            else:
                polarity = diff + 2
            print(polarity)

    return utterances, polarity, success


def g_read_files(rep):
    for file in glob(rep + "**/*.json", recursive=True):
        if "label.json" in file:
            yield json.load(open(file))


def get_dials(fic, l):
    for elem in getConvs(fic):
        l.append(elem)
    return l


def rewrite(flist, dials, outnormal, outerr):
    i = 0
    err = 0
    succ = 0
    for fic in g_read_files(flist):
        i += 1
        print(i)
        ut, pol, suc = open_dstc_dial(fic)
        complete = False
        assoc = []
        for elem in ut:
            k = 0
            for dial in dials:
                k += 1
                d = Dialog(dial)
                new_d = [elem.splitted[0] for elem in d.new if
                         '\t' in elem.utterance and "<SILENCE>" not in elem.utterance]
                first = new_d[0]
                s = 0
                if "<SILENCE>" in first:
                    s += 1
                if Levenshtein.distance(elem, first) < 3:
                    j = 0

                    for turn in ut[1:]:
                        j += 1
                        if len(new_d) < 2:
                            complete = False
                            break
                        if Levenshtein.distance(turn, new_d[j]) < 2:
                            complete = True
                            # sys.exit()
                        else:
                            complete = False
                            break

                else:
                    continue
                if complete:
                    assoc = d
                    assoc.no_change()
                    nbr = len(assoc.changed.split('\n'))
                    assoc.changed += f"{nbr} {pol}\t{suc}\n"
                    dials.remove(dial)
                    break
            if complete:
                break

        if not complete:

            err += 1
        else:
            succ += 1
            outnormal.write(assoc.changed)
            outnormal.write('\n')

    for dial in dials:
        d = Dialog(dial)
        d.no_change()
        nbr = len(d.changed.split('\n'))
        d.changed += f"{nbr} 0\tUNK\n"
        outerr.write(d.changed)
        outerr.write('\n')
        # if i == 12:
        #     sys.exit()
    print(err)
    print(succ)
    print(i)


def get_dials(file):
    dialogues = []
    dialog = []
    for line in file.readlines():
        if len(line) == 1:
            dialogues.append(dialog)
            dialog = []
        else:
            dialog.append(line.rstrip())
    return dialogues


if __name__ == '__main__':
    splitter = ["train", "dev", "test"]

    dsc = "../../diaser/expe2/data/dstccamrest.json"
    ontology = "../../wmbot/wmm10/data/dialog-bAbI-tasks/ontology.json"
    mwoz22 = "../../multiwoz/data/MULTIWOZ2.1/data.json"
    mwoz23 = "../../multiwoz/data/MULTIWOZ2.3/data.json"
    mwoz24 = "../../multiwoz/data/MULTIWOZ2.4/data.json"
    any = {}
    dom = {}
    inte = {}
    inf = {}
    reqs = {}
    domint = {}
    dominf = {}
    domreq = {}
    intinf = {}
    intreq = {}
    infreq = {}
    domintinf = {}
    domintreq = {}
    dominfreq = {}
    intinfreq = {}
    shortall = {}
    errs = 0
    total = 0
    empty = 0
    for elem in splitter:
        dias = f"../../diaser/processed_data/camrest_all_split/{elem}.json"
        empty, errs, total = get_mwoz_diffs(mwoz22, mwoz23, mwoz24, dias, shortall, any, dom, inte, inf, reqs, domint,
                                            dominf, domreq, intinf, intreq, infreq, domintinf, domintreq, dominfreq,
                                            intinfreq, errs, total, empty)
    print(f"errs = {errs}, total = {total}, empty = {empty}")
    json.dump(any, fp=open('../../consistency/data/any.json', 'w'), indent=4)
    json.dump(dom, fp=open('../../consistency/data/dom.json', 'w'), indent=4)
    json.dump(inte, fp=open('../../consistency/data/intents.json', 'w'), indent=4)
    json.dump(inf, fp=open('../../consistency/data/informable.json', 'w'), indent=4)
    json.dump(reqs, fp=open('../../consistency/data/requestable.json', 'w'), indent=4)
    json.dump(domint, fp=open('../../consistency/data/domint.json', 'w'), indent=4)
    json.dump(dominf, fp=open('../../consistency/data/dominf.json', 'w'), indent=4)
    json.dump(domreq, fp=open('../../consistency/data/domreq.json', 'w'), indent=4)
    json.dump(intinf, fp=open('../../consistency/data/intinf.json', 'w'), indent=4)
    json.dump(intreq, fp=open('../../consistency/data/intreq.json', 'w'), indent=4)
    json.dump(infreq, fp=open('../../consistency/data/infreq.json', 'w'), indent=4)
    json.dump(domintinf, fp=open('../../consistency/data/domintinf.json', 'w'), indent=4)
    json.dump(domintreq, fp=open('../../consistency/data/domintreq.json', 'w'), indent=4)
    json.dump(dominfreq, fp=open('../../consistency/data/dominfreq.json', 'w'), indent=4)
    json.dump(intinfreq, fp=open('../../consistency/data/intinfreq.json', 'w'), indent=4)
    json.dump(shortall, fp=open('../../consistency/data/intersection.json', 'w'), indent=4)

    # get_polarity(open(dias), open(dsc), json.load(open(ontology)))
