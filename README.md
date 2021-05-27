# EmployeePointsAPI
A simple API to keep track of points awarded to employees for fixing bugs

### Struktura projektu:

#### Slozka models

Ve slozce models jsou datove modely, ktere jsem vytvoril pro zamestance, aplikace, body a pro mesice, pro ktere budou vypisovani vitezi. Kazdy model ma jeden file, ktery se jmenuje stejne jako model samotny. 

Modely jsou vytvoreny pomoci library MongoEngine, jelikoz jsem z frameworku Django zvykly na ORM. Modely, ktere bych povazoval za zajimave jsou zejmena PeriodWinners a Points. Jsou nastaveny tak, aby splnily zadani - napriklad body lze vkladat zpetne, mame zde pro Points dva ruzne udaje pro date_earned a date_added. Model Points ma pak take ReferenceField na Employee - odkaz na zamestnance, kteremu byl bod udelen a ReferenceField na Application - odkaz na aplikaci, za kterou byl bod udelen. Toto jsem udelal podobnym stylem jako by v SQL databazi bylo prideleni ForeignKey. Last, but not least ma Points model take BooleanField prod_env, aby bylo mozne rozdelit body pro produkcni a pred produkcni prostredi.

Model PeriodWinners ma reprezentovat jednotlive mesice a jejich viteze. Kdyz jsem u sebe testoval, nastavil jsem si zde napriklad periodu, ktere jsem dal jmeno "May 2021", dal ji prislusny start_date (2021-05-01) a end_date (2021-31-05), a inicialne jsem nastavil evaluated jako False a winner jako Null. Periodu pak lze vyhodnotit, coz zmeni hodnotu evaluated na True, a vlozi referenci na zamestnance, ktery tuto periodu vyhral.

Dalsi modely - Employees a Applications jsou velice jednoduche a nestoji moc za vysvetleni. Mozna u Employees bych vyzdvihnul pole active, ktere je True nebo False, podle toho jestli zamestnanec je stale ve firme nebo ne, coz umoznuje trackovani historickych dat, dle zadani.

#### Slozka api

Ve slozce api jsou pak definovany namespace - moduly API, ktere zpracovavaji individualni HTTP requesty a responses. Zde je implementovana logika pridavani zamestnancu, aplikaci, bodu a vyhodnocovani period. Opet bych rekl ze nejzajimavejsi zde jsou Point a PeriodWinner, ktere implementuji logiku zadanou v zadani - napriklad ze body nelze pripisovat za periody, ktere jsou jiz vyhodnocene, nebo losovani vitezu, kde se vitezem stava bud zamestnanec, ktery ma nejvic bodu, nebo losovani nahodneho zamestnance ze zamestnancu, kteri maji nejvyssi pocet bodu, pokud jich je vic.

Zde bych vyzdvihnul, ze api jsou naprogramovana tak, aby flask-restx implementoval swagger-json dokumentaci. Takze kdyz si projekt spustite, a pres prohlizec navstivite index (127.0.0.1:5000/), tak je zde krasna dokumentace ohledne toho jake HTTP requesty lze posilat na ktera URL, co se ocekava za data, a jakou formu bude mit response. 

#### Hlavni slozka

Ve hlavni slozce pak jeste mame app.py, ve kterem je nakonfigurovana samotna Flask aplikace. Zde stoji za zminku default_config. Pokud byste si aplikaci chtel sam spustit, tak je potreba mit pusteny MongoDB server s prislusnym hostem a portem, s databazi jmenem employeepoints. V teto databazi by pak meli byt 4 collections, jedna pro kazdy model - applications, employees, period_winners a points. Ale pokud si projekt sam spustite, a pres POST requesty pridate zamestnance, body, periody a aplikace, tak by se vam tyto collections meli inicializovat sami v databazi. 

Poslednim filem je setup.py, ktery by mel umoznit snadnou instalaci projektu pres pip, ale to jsem nemel moznost otestovat. Alternativne je mozne aplikaci spustit pomoci prikazu 'py app.py' (na Windows), ktery by pak mel rozbehnout lokalni server. 

#### Requirements

Ke spusteni aplikace je potreba mit nainstalovany: Flask, flask-restx a MongoEngine. 

