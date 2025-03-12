from flask import Flask, render_template, request, redirect, url_for, flash, session
app = Flask(__name__)
app.secret_key = 'your_secret_key'


from copy import deepcopy
 
def copy_automate(automate):
    return Automate(automate.alphabet,
                    automate.etats,
                    automate.etats_initiaux,
                    automate.etats_finaux,
                    automate.table_de_transition)


def complete_AFD_transformation(AFD):
    resultat = copy_automate(AFD)
    
    def colle_etats(etats_AFD): #{2, 3} => {'2, 3'}, [{2}, {2, 3}] => {'2', '2, 3'}
        if type(etats_AFD) == type(set()):
            return {"".join(str(etats_AFD)[1:-1].split(" "))}
        else:
            resultat = set()
            for etat_AFD in etats_AFD:
                resultat = resultat | colle_etats(etat_AFD)
            return resultat
    
    resultat.etats = colle_etats(resultat.etats)
    resultat.etats_initiaux = colle_etats(resultat.etats_initiaux)
    resultat.etats_finaux = colle_etats(resultat.etats_finaux)
    resultat.table_de_transition = [{'origines':colle_etats(transition['origines']), 'lettre':transition['lettre'], 'destinations':colle_etats(transition['destinations'])} for transition in resultat.table_de_transition]    
    return resultat

def str_table_transition(table_de_transition):
    chaine = "    [\n"
    for el in table_de_transition:
        chaine += "        " + str(el) + "\n"
    chaine += "    ]"
    return chaine
    
class Automate:
    
    alphabet = set() # L'alphabet est une liste de symbole ex: {'a', 'b'}
    etats = set() # L'ensemble des états est une liste de symbole ex: {0, 1, "a", "b", 2}
    etats_initiaux = set() # Les états initiaux sont une partie des états
    etats_finaux = set()
    table_de_transition = [] # liste de dictionnaire ex: [{'origines':{0}, 'lettre':'a', 'destinations':{1, 2}}, {'origines':{0, 1}, 'lettre':'a', 'destinations':{1, 2, 3}}  ...,]
    
    def __init__(self, alphabet, etats, etats_initiaux, etats_finaux, table_de_transition):
        self.alphabet = deepcopy(alphabet)
        self.etats = deepcopy(etats)
        self.etats_initiaux = deepcopy(etats_initiaux)
        self.etats_finaux = deepcopy(etats_finaux)
        self.table_de_transition = deepcopy(table_de_transition)
    
    def __str__(self):
        resultat = f"\n  ----Alphabet---------------: {self.alphabet}\n  ----Etats------------------: {self.etats}\n  ----Etats initiaux---------: {self.etats_initiaux}\n  ----Etat finaux------------: {self.etats_finaux}\n  ----Table de transition----:\n"
        return resultat + str_table_transition(self.table_de_transition)
    
    def transiter(self, etats, lettres):
        resultat = set()
        if type(lettres) != type(set()) and type(lettres) != type(list()):
            lettres = {lettres}
        for etat in etats:
            for lettre in lettres:
                for transition in self.table_de_transition:
                    if etat in transition['origines'] and transition['lettre'] == lettre:
                        resultat = resultat | transition['destinations']
                        break
        return resultat
    
    def eFermeture(self, etats):
        etats_marques = set() # representent la variable qui contiendra le resultat recherché
        etats_non_marques = deepcopy(etats)
        while len(etats_non_marques) != 0:
            passe = self.transiter(etats_non_marques, lettres='')
            etats_marques = etats_marques | etats_non_marques
            etats_non_marques = passe.difference(etats_marques)
        return etats_marques
            
    def transition_existante(self, etat, lettre):
        for transition in self.table_de_transition:
            if etat in transition['origines'] and transition['lettre'] == lettre:
                return True
        return False
    
    def est_eAFN(self):
        for lettre in self.alphabet:
            if lettre == '':
                return True
        return False
    
    def est_AFN(self):
        return not self.est_eAFN()
        
    def est_AFD(self):
        return self.est_AFN() and self.est_deterministe()
    
    def est_deterministe(self):
        if self.est_eAFN():
            return False
        else:
            for etat in self.etats:
                etat = {etat}
                for lettre in self.alphabet:
                    if len(self.transiter(etat, lettre)) > 1:
                        return  False
        return True
    
    def est_complet(self):
        for etat in self.etats:
            for lettre in self.alphabet:
                if not self.transition_existante(etat, lettre):
                    return False
        return True
                    
    def nature(self):
        ressult = ''
        if self.est_eAFN():
            resultat = "e-AFN (Automate Fini Non-deterministe à Transitions spontannées)"
        else:
            if self.est_deterministe():
                r1 = "AFD"
                r2 = "Automate Fini Deterministe"
            else:
                r1 = "AFN"
                r2 = "Automate Fini Non-deterministe"
                
            if self.est_complet():
                r1 += "C"
                r2 += " Complet"
            else:
                r1 += "P"
                r2 += " Partiel"
            
            resultat = f"{r1} ({r2})"
        return resultat
    
    def vers_unique_etat_initial(self):
        resultat = copy_automate(self)
        if len(resultat.etats_initiaux) > 1:
            etat_initial = {min(resultat.etats_initiaux)}
            for etat in resultat.etats_initiaux:
                if etat != etat_initial:
                    resultat.table_de_transition.append({'origines':etat_initial, 'lettre':'', 'destinations':set(etat)})
            resultat.etats_initiaux = etat_initial
        return resultat
                        
    def vers_AFN(self):
        resultat = copy_automate(self)
        if self.est_eAFN():
            resultat = resultat.vers_unique_etat_initial()
            new_table_de_transition = []
            etat_marques = set()
            etats_non_marques = resultat.etats_initiaux
            etats_finaux = set()
            while len(etats_non_marques) != 0:
                passe = set()
                for etat in etats_non_marques:
                    etat = {etat}
                    epsilon_fermetures = resultat.eFermeture(etat)
                    if len(epsilon_fermetures & resultat.etats_finaux) != 0:
                        etats_finaux = etats_finaux | etat
                    for lettre in resultat.alphabet:
                        if lettre != '':
                            etat_transiter = resultat.transiter(epsilon_fermetures, lettre)
                            
                            
                            if len(etat_transiter) != 0:
                                new_table_de_transition.append({'origines':etat, 'lettre':lettre, 'destinations':etat_transiter})
                                passe = passe | etat_transiter
                                
                etat_marques = etat_marques | etats_non_marques
                etats_non_marques = passe.difference(etat_marques)
            alphabet = deepcopy(self.alphabet)
            alphabet.remove('')
            resultat = Automate(alphabet, resultat.etats, resultat.etats_initiaux, etats_finaux, new_table_de_transition)
        return resultat

    def vers_AFD(self):
        resultat = copy_automate(self)
        if resultat.est_eAFN():
            resultat = resultat.vers_AFN()
        if not resultat.est_AFD():
            new_table_de_transition = []
            etats_marques = []
            etats_non_marques = [self.etats_initiaux]
            etats_finaux = []
            while len(etats_non_marques) != 0:
                passe = []
                for etat in etats_non_marques:
                    if len([e for e in etat if e in resultat.etats_finaux]) != 0 and etat not in etats_finaux:
                        etats_finaux.append(etat)
                    for lettre in resultat.alphabet:
                        etat_transiter = resultat.transiter(etat, lettre)
                        
                        
                        if len(etat_transiter) != 0:
                            new_table_de_transition.append({'origines':etat, 'lettre':lettre, 'destinations':etat_transiter})
                            if etat_transiter not in passe:
                                passe = passe + [etat_transiter]
                                
                etats_marques = etats_marques + [etat for etat in etats_non_marques if etat not in etats_marques]
                etats_non_marques = [etat for etat in passe if etat not in etats_marques]
    
                    
            resultat = complete_AFD_transformation(Automate(resultat.alphabet, etats_marques, [resultat.etats_initiaux], etats_finaux, new_table_de_transition))
        return resultat

    def vers_automate_complet(self):
        resultat = copy_automate(self)

        nom_etat = 'p'
        i = 1
        while nom_etat in resultat.etats:
            nom_etat = 'p_' + str(i)
            i += 1
        etat_puit = {nom_etat}
        for lettre in resultat.alphabet:
            if lettre != '':
                resultat.table_de_transition = resultat.table_de_transition + [{'origines': etat_puit, 'lettre': lettre, 'destinations': etat_puit}]
                for transition in resultat.table_de_transition:
                    if len(resultat.transiter(transition['origines'], lettre)) == 0:
                        resultat.table_de_transition = resultat.table_de_transition + [{'origines': transition['origines'], 'lettre': lettre, 'destinations': etat_puit}]
        return resultat
    
    def vers_AFDC(self):
        return self.vers_AFD().vers_automate_complet()
    
    def vers_automate_canonique(self):
        #idex_des_sous_groupes_contenant_les_etats idsgcle
        def idsgcle(groupes_etats, etats):
            resultat = set()
            for sous_groupe in groupes_etats:
                for etat in etats:
                    if etat in sous_groupe:
                        resultat = resultat | {groupes_etats.index(sous_groupe)}
            return resultat
        
        #des_sous_groupes_contenant_les_etats dsgcle
        def sgcle(groupes_etats, etats):
            resultat = []
            for sous_groupe in groupes_etats:
                for etat in etats:
                    if etat in sous_groupe and sous_groupe not in resultat:
                        resultat = resultat + [sous_groupe]
            return resultat
        
        new_table_de_transition = []
        etats_initiaux = []
        etats_finaux = []
        resultat = copy_automate(self)
        groupes_etats = [resultat.etats.difference(resultat.etats_finaux), resultat.etats_finaux]
        stabilite_atteinte = False
        while not stabilite_atteinte:
            passe = {'index_groupes_atteint':[], 'etats_de_depart':[]} # ex de structure {'index_groupes_atteint':[{0}, {1, 2, 3}], 'etats_de_depart':[{1, 2}, {2, 7}]}
            for sous_groupe in groupes_etats:
                passe2 = {'index_groupes_atteint':[], 'etats_de_depart':[]}
                for etat in sous_groupe:
                    etat = {etat}
                    trans = resultat.transiter(etat, resultat.alphabet)
                    index_groupes = idsgcle(groupes_etats, trans)
                    if index_groupes in passe2['index_groupes_atteint']:
                        position_groupe = passe2['index_groupes_atteint'].index(index_groupes)
                        passe2['etats_de_depart'][position_groupe] = passe2['etats_de_depart'][position_groupe] | etat
                    else:
                        passe2['index_groupes_atteint'] = passe2['index_groupes_atteint'] + [index_groupes]
                        passe2['etats_de_depart'] = passe2['etats_de_depart'] + [etat]
                passe['index_groupes_atteint'] = passe['index_groupes_atteint'] + passe2['index_groupes_atteint']
                passe['etats_de_depart'] = passe['etats_de_depart'] + passe2['etats_de_depart']
            new_groupes_etats = passe['etats_de_depart']
            if new_groupes_etats == groupes_etats:
                stabilite_atteinte = True
            else:
                groupes_etats = new_groupes_etats
        for sous_groupe in groupes_etats:
            if len([el for el in sous_groupe if el in resultat.etats_finaux]) != 0:
                etats_finaux.append(sous_groupe)
            if len([el for el in sous_groupe if el in resultat.etats_initiaux]) != 0:
                etats_initiaux.append(sous_groupe)
            for lettre in resultat.alphabet:
                trans = resultat.transiter(sous_groupe, lettre)
                groupes_ateint = sgcle(groupes_etats, trans)
                new_table_de_transition.append({'origines':sous_groupe, 'lettre':lettre, 'destinations':groupes_ateint})
        resultat = complete_AFD_transformation(Automate(resultat.alphabet, groupes_etats, etats_initiaux, etats_finaux, new_table_de_transition))
        return resultat
       
    def decompose_mot_en_lettre(self, mot):
        
        chaine_symbole = ''.join(self.alphabet)
        for key, symbole in enumerate(mot):
            if symbole not in chaine_symbole:
                raise MotInvalide(mot, key)
            
        if mot == "":
            return []
        elif mot in self.alphabet: # Le mot est soit vide soit une lettre de l'alphabet
            return [mot]
        else:
            lettre = mot[0]; mot = mot[1:]
            while lettre not in  self.alphabet and len(mot) != 0:
                lettre += mot[0]; mot = mot[1:]
            r1 = []
            if lettre in self.alphabet:
                r1 = [lettre]
            if len(mot) == 0:
                return r1
            else:
                return r1 + self.decompose_mot_en_lettre(mot)

    def reconnait_le_mot(self, mot):
        AFDC_correspondant = self.vers_AFDC()
        lettres = self.decompose_mot_en_lettre(mot)
        position = AFDC_correspondant.etats_initiaux
        for lettre in lettres:
            position = AFDC_correspondant.transiter(position, lettre)
        if list(position)[0] in AFDC_correspondant.etats_finaux:
            return True
        return False
    

class MotInvalide(Exception):
    def __init__(self, mot, position_de_erreur):
        self.mot = mot
        self.position_de_erreur = position_de_erreur
        
        message = "Caractère illicite détecté "+ self.mot
        message += "\n" + ' ' * (self.position_de_erreur + 58) + '^'
        
        return super().__init__(message)
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_automate', methods=['POST'])
def create_automate():
    alphabet = request.form.get('alphabet').split(',')
    etats = set(request.form.get('etats').split(' '))
    etats_initiaux = set(request.form.get('etats_initiaux').split(' '))
    etats_finaux = set(request.form.get('etats_finaux').split(' '))

    origines = request.form.getlist('origine[]')
    lettres = request.form.getlist('lettre[]')
    destinations = request.form.getlist('destinations[]')
    transitions = []

    for i in range(len(origines)):
        transition = {
            'origines': origines[i],
            'lettre': lettres[i],
            'destinations': destinations[i]
        }
        transitions.append(transition)

    session['automate'] = {
        'alphabet': alphabet,
        'etats': list(etats),
        'etats_initiaux': list(etats_initiaux),
        'etats_finaux': list(etats_finaux),
        'table_de_transition': transitions
    }

    return redirect(url_for('operations'))

@app.route('/operations')
def operations():
    data = session.get('automate')
    if not data:
        return redirect(url_for('index'))

    automate = Automate(data['alphabet'], set(data['etats']), set(data['etats_initiaux']),
                        set(data['etats_finaux']), data['table_de_transition'])
    return render_template('operations.html', automate = automate)

@app.route('/execute_action', methods=['POST'])
def execute_action():
    action = request.form.get('action')
    data = session.get('automate')
    if not data:
        return redirect(url_for('index'))

    automate = Automate(data['alphabet'], set(data['etats']), set(data['etats_initiaux']),
                        set(data['etats_finaux']), data['table_de_transition'])

    if action == 'nature':
        result = automate.nature()
    elif action == 'eFermeture':
        etats = request.form.get('etats')
        etats = {e for e in etats.split(' ')}
        result = automate.eFermeture(etats)
    elif action == 'decompose':
        mot = request.form.get('mot')
        result = automate.decompose_mot_en_lettre(mot)
    elif action == 'reconnaitre':
        mots = request.form.getlist('mots[]')
        result = {mot: automate.reconnait_le_mot(mot) for mot in mots}
    elif action == 'vers_AFN':
        result = automate.vers_AFN()
    elif action == 'vers_AFD':
        result = automate.vers_AFD()
    elif action == 'vers_AFC':
        result = automate.vers_automate_complet()
    elif action == 'vers_automate_canonique':
        result = automate.vers_automate_canonique()
    else:
        result = "Action non reconnue"

    return render_template('result.html', action=action, result=result, automate = automate)

if __name__ == '__main__':
    app.run(debug=True)

