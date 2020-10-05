# all existing addresses
CSV_PATH_1 = '/home/robert/Documents/redo2oo/kunden/fernuni/data/addressen_email_usw_okt_4.csv'
# media addresses
CSV_PATH_2 = '/home/robert/Documents/redo2oo/kunden/fernuni/data/Medien - Jahresbericht_okt_1.csv'
# output file
CSV_PATH_3 = '/home/robert/Documents/redo2oo/kunden/fernuni/data/addressen_media_okt_4.csv'

import csv
# all existing addresses
HEADER1 = ['id', 'name', 'last_name', 'street', 'street2', 'zip', 'city', 'email', 'lang']
# media addresses
HEADER2 = ['LANG', 'ANREDE', 'FUNKTION', 'NAME', 'VORNAME', 'STREET', 'STREET2', 'PLZ', 'ORT', 'FUNKTION', 'MAILADRESSE']

LINE = "%(ID)s,%(LANG)s,%(company_type)s,%(ANREDE)s,%(NAME)s,%(VORNAME)s,%(STREET)s,%(STREET2)s,%(PLZ)s,%(ORT)s,%(MAILADRESSE)s,Jahresbericht,Medien\n"
FIRST_LINE = "id,Language,company_type,Title,Last name,Name,Street,Street2,Zip,City,email,tags,tags\n"
LANGUAGES = {'d' : 'German / Deutsch', 'f' : 'French (CH) / Français (CH)'}
START_AT  = 2 # where to start to read

def write_rec(out_file, rec, old_id):
    """
    write content of rec to outfile, depending on old_id add also existing id
    """
    # Make sure there are no extra spaces
    for k,v in rec.items():
        try:
            rec[k] = v.strip()
        except:
            pass
        
    # if there is an old id, we update an existing record
    rec['ID'] = old_id
    # set the language
    rec['LANG'] = LANGUAGES.get(rec['LANG'], '')
    # if there is an Anrede, the record represents a person
    if rec['ANREDE']:
        rec['company_type'] = 'Individual'
        rec['ANREDE'] = '' # got an error of duplicate title for record
    else:
        rec['company_type'] = 'Company'
    out_file.write(LINE % rec)

ALL_RECS = {}
with open(CSV_PATH_1) as csv_file:
    csv_reader = csv.DictReader(csv_file, fieldnames=HEADER1, delimiter=',')
    for rec in csv_reader:
        email = rec['email'].lower()
        if email:
            ALL_RECS[email] = rec
            
with open(CSV_PATH_3, 'w') as out_file:
    # loop over file with media addresses
    out_file.write(FIRST_LINE)
    with open(CSV_PATH_2) as csv_file:
        count_f = 0
        count_nf = 0
        csv_reader = csv.DictReader(csv_file, fieldnames=HEADER2, delimiter=',')
        for rec in csv_reader:
            if csv_reader.line_num < START_AT:
                continue # skip first line with header and earlier chunks
            email = rec['MAILADRESSE'].lower()
            if email in ALL_RECS.keys():
                print(email)
                count_f += 1
                old_id = ALL_RECS[email]['id']
                write_rec(out_file, rec, old_id)
            else:
                print('hoppla schorsch:', email)
                count_nf += 1
                write_rec(out_file, rec, '')
            
print(count_f, count_nf)            