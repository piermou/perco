import time

from bs4 import BeautifulSoup
from curl_cffi import requests

response = requests.get(
    url="https://www.vinted.fr/items/6957177115-our-legacy-workshop-overdyed-denim?referrer=catalog"
)
# with open("page.html", "r", encoding="utf-8") as f:
#     html = f.read()
#
print(response.status_code)

start = time.time()
soup1 = BeautifulSoup(response.text, "html.parser")
print("html.parser:", time.time() - start)

# lxml
start = time.time()
soup2 = BeautifulSoup(response.text, "lxml")
print("lxml:", time.time() - start)

soup = BeautifulSoup(response.text, "html.parser")

mama = soup.find_all(
    "div",
    {"class": "item-photos"},
)

wow = mama[0].find_all("img")
for i in wow:
    print(i.get("src"))

bobo = soup.find(
    "span",
    class_="web_ui__Text__text web_ui__Text__body web_ui__Text__left web_ui__Text__format",
)

for a in bobo.find_all("a"):
    a.decompose()

import re


def nettoyer_description(text):
    text = text.replace("⸻", "")  # Enlève le séparateur
    text = re.sub(
        r"\s+", " ", text
    )  # Remplace tous les espaces multiples (espaces, sauts de ligne, tab, etc.) par un seul
    return text.strip()


description = bobo.get_text(separator="\n").strip()
text = nettoyer_description(description)
print(text)


# dodo = soup.find("div", class_="details-list details-list--main-info")

titre = soup.select_one(
    'div[data-testid="item-page-summary-plugin"] span.web_ui__Text__title'
)
titre = titre.text.strip() if titre else None

# Taille
taille = soup.select_one('div[data-testid="item-attributes-size"] .web_ui__Text__bold')
taille = taille.text.strip().replace("\n", "") if taille else None

# État
etat = soup.select_one('div[data-testid="item-attributes-status"] .web_ui__Text__bold')
etat = etat.text.strip() if etat else None

# Marque
marque = soup.select_one('div[data-testid="item-attributes-brand-menu-button"]')
if not marque:
    marque = soup.select_one('[itemprop="name"]')
marque = marque.text.strip() if marque else None

# Prix
prix = soup.select_one('div[data-testid="item-price"] p')
prix = prix.text.strip() if prix else None

# Prix avec protection
prix_protection = soup.select_one('button[aria-label*="Protection acheteurs"] div')
prix_protection = prix_protection.text.strip() if prix_protection else None

# Couleur
couleur = soup.select_one(
    'div[data-testid="item-attributes-color"] .web_ui__Text__bold'
)
couleur = couleur.text.strip() if couleur else None

# Nombre de vues
vues = soup.select_one(
    'div[data-testid="item-attributes-view_count"] .web_ui__Text__bold'
)
vues = vues.text.strip() if vues else None

# Membres intéressés
interesses = soup.select_one(
    'div[data-testid="item-attributes-interested"] .web_ui__Text__bold'
)
interesses = interesses.text.strip() if interesses else None

# Date d'ajout
date_ajout = soup.select_one(
    'div[data-testid="item-attributes-upload_date"] .web_ui__Text__bold'
)
date_ajout = date_ajout.text.strip() if date_ajout else None

# Résumé des infos
info = {
    "Titre": titre,
    "Taille": taille,
    "État": etat,
    "Marque": marque,
    "Prix": prix,
    "Prix avec protection": prix_protection,
    "Couleur": couleur,
    "Vues": vues,
    "Intéressés": interesses,
    "Ajouté": date_ajout,
}

for key, value in info.items():
    print(f"{key}: {value}")


# Pseudo
username = soup.find("span", {"data-testid": "profile-username"})
pseudo = username.text.strip() if username else None

# 2. Lien de profil
profile_link = soup.find("a", class_="web_ui__Cell__link")
link = "https://www.vinted.fr" + profile_link.get("href") if profile_link else None

# Photo de profil
img_tag = soup.find("img", class_="web_ui__Image__content")
photo_url = img_tag.get("src") if img_tag else None

# Note
rating_group = soup.find("div", {"role": "group"})
note = rating_group.get("aria-label") if rating_group else None

# Nombre d’évaluations
review_count_tag = soup.find("div", class_="web_ui__Rating__label")
review_count = review_count_tag.text.strip() if review_count_tag else None

# Badge pro ?
badge_tag = soup.find("div", {"data-testid": "seller-pro-badge--content"})
badge = badge_tag.text.strip() if badge_tag else None

#  Ville
city_container = soup.find(
    "div", string="Pantin, France"
)  # ou cherche plus finement si besoin

# Affichage
print("Pseudo :", pseudo)
print("Lien :", link)
print("Photo :", photo_url)
print("Note :", note)
print("Avis :", review_count)
print("Badge :", badge)
print("Ville :", city_container)

# text = city_container.get_text(strip=True)
pays = text.split(",")[-1].strip() if "," in text else None

print(pays)

# print(type(city_container))

# for block in mama:
#     imgs = block.find_all("img")


#

# for img in soup.find_all("img"):
#     print(img.get("src"))
#
#
