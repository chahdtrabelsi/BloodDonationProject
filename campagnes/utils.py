from accounts.utils import groupes_compatibles

def est_compatible_groupe(donneur, campagne):

    if not campagne.groupes_cibles:
        return True

    groupes_autorises = []

    groupes_campagne = [
        g.strip() for g in campagne.groupes_cibles.split(",")
    ]

    for g in groupes_campagne:
        groupes_autorises.extend(groupes_compatibles(g))

    return donneur.groupe_sanguin in groupes_autorises
def groupes_compatibles(groupe):
    compat = {
        'O-': ['O-', 'O+', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }
    return compat.get(normalize_group(groupe), [])
def normalize_group(g):
    return g.strip().upper()