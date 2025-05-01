# ClipRocks

<div align="center">
<a href="./readme.md"><strong>English</strong></a> | <strong>Français</strong>
</div>

---

## 🎁 Introduction

**ClipRocks** est un moteur de scripts et de plugins pour DaVinci Resolve.

Cliprocks permet de copier des images, des vidéos ou d'autres éléments interactifs depuis votre ordinateur ou le web, et de les coller directement dans votre timeline DaVinci Resolve. Les médias peuvent éventuellement être traités par l'IA—par exemple, pour supprimer les arrière-plans ou améliorer les images—avant l'insertion.

Ce projet est encore en évolution. Il est partagé ici dans l'espoir qu'il puisse aider les autres.

J'offre cet outil aux personnes qui en ont besoin. <br>
N'oubliez pas : je n'ai aucune obligation. <br>

---

## ✨ Fonctionnalités

- Collez des images ou des vidéos directement dans la timeline de Resolve
- Suppression de l'arrière-plan alimentée par l'IA (optionnelle)
- Mise à l'échelle alimentée par l'IA (optionnelle)
- Prend en charge le contenu provenant de pages web ou d'applications locales

---

## 🛠 Installation du moteur (en construction 🚧)

### ✅ 1. Téléchargement
___
```cmd
cd /d "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\"
git clone https://github.com/coderocksAI/ClipRocks.git
```
📌 Le dossier Comp doit contenir le dossier ClipRocks, et non ses fichiers directement. (Exemple : \Comp\ClipRocks\cliprocks.py)


### ✅ 2. Création de config.conf (chemin des modules, assets, etc)
___
📌 Ce fichier est généré automatiquement au premier lancement du script.
Il contient les chemins de base du plugin (modules, assets, venv, etc.) que vous pourrez personnaliser ensuite.

1.  Lancez le script une première fois pour générer le fichier de configuration.
Dans DaVinci Resolve, allez dans :
`Workspace > Scripts > Comp > Cliprocks > cliprocks`

2.  Un fichier config.conf sera alors créé automatiquement à cet emplacement : 
```bat
C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\ClipRocks\config.conf
```

### ✅ 3. Préparation de l’environnement Python (venv)
___
1. Ouvrez le fichier config.conf généré précédemment et repérez la valeur de la clé venv.
Ce chemin correspond à l’endroit où seront installés les modules Python nécessaires au bon fonctionnement du plugin.

2. Depuis une console (cmd), appliquez soigneusement les commandes suivantes, une par une :

```bat
cd /d "chemin\vers\le\dossier"
python -m venv venv
venv\Scripts\activate
pip install pillow requests
```
___

## 🛠 Utilisation du moteur
Pour activer rapidement le menu contextuel de ClipRocks, vous pouvez créer un raccourci clavier dans DaVinci Resolve.  
Choisissez la touche de votre choix, puis copiez une image depuis votre navigateur web.  
Appuyez ensuite sur votre raccourci : le menu contextuel du script se lancera automatiquement avec l’image détectée.

## ⚠️ Limites de DaVinci Resolve
Le script a été conçu pour fonctionner à la fois avec la version gratuite et la version Studio de DaVinci Resolve.  Cependant, depuis la version 19+, Blackmagic a supprimé l’accès à l’API graphique dans la version gratuite. Cela implique quelques contraintes fonctionnelles.

➡️ **Important** : vous devez activer manuellement le script à chaque lancement de DaVinci.  
Rendez-vous dans le menu : `Workspace > Scripts > Comp > Cliprocks > cliprocks`. Ensuite, enjoy, la touche raccourcie prend le relais.

## 🤝 Contributions

Ce projet n'est pas activement à la recherche de contributions, mais les retours réfléchis sont toujours les bienvenus.

---

## Notes

- L'intégration de l'IA repose sur un traitement local. Aucune donnée n'est envoyée en ligne.
- Certaines fonctionnalités peuvent évoluer en fonction des priorités de développement.

---

## 📜 Licence

Licence GPL-3.0 — voir `LICENSE.md` pour plus de détails.

---