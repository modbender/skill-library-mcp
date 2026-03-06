# Documentation de Free Mobile pour l’envoi de SMS

- [Docmentation pour les abonnés Free Mobile](https://mobile.free.fr/account/mes-options/notifications-sms)

---

## Notifications par SMS

Envoyez des notifications par SMS sur votre propre mobile via n'importe quel équipement connecté à internet.


Vous pouvez, par exemple, configurer une centrale d'alarme ou un NAS (type Synology) à votre domicile de telle sorte qu'ils envoient un SMS sur votre téléphone Free Mobile lorsqu'un événement se produit.

*Ce service n'est PAS fait pour créer des listes de diffusion, c'est à dire envoyer des SMS à un groupe de personnes.*

L'envoi du SMS se fait en appelant le lien suivant : `https://smsapi.free-mobile.fr/sendmsg`

avec les paramètres suivants :

- `user` : votre login
- `pass` : votre clé d'identification générée automatiquement par notre service
- `msg` : le contenu du SMS encodé sous forme d'url (Percent-encoding)


Exemple : Envoyer le message "Hello World !" sur votre mobile :

`https://smsapi.free-mobile.fr/sendmsg?user=12345678&pass=XXXXXXXXXXXXXX&msg=Hello%20World%20!`

Vous pouvez également, si vous le préférez, envoyer les paramètres en POST.
Dans ce cas, le contenu du message n'a pas besoin d'être encodé. 

Le code de retour HTTP indique le succès ou non de l'opération :

- `200` : Le SMS a été envoyé sur votre mobile.
- `400` : Un des paramètres obligatoires est manquant.
- `402` : Trop de SMS ont été envoyés en trop peu de temps.
- `403` : Le service n'est pas activé sur l'Espace Abonné, ou login / clé incorrect.
- `500` : Erreur côté serveur. Veuillez réessayer ultérieurement.

*Votre clé d'identification est propre à votre ligne et change à chaque activation de l'option. Ne la communiquez pas à une tierce personne.*

Prix de l'option : Offerte 
