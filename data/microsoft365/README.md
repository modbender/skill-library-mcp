# Custom Microsoft Integration (Device Code Flow)

Dit script biedt een veilige, lokale integratie met Microsoft Graph (Outlook, Agenda, Contacten, OneDrive) zonder externe servers of complexe redirects.

## Veiligheid

- **Lokaal**: Alle tokens worden lokaal opgeslagen in `tokens.json`.
- **Transparant**: De code is open source en maakt directe calls naar Microsoft Graph.
- **Geen externe proxy**: Gebruikt de Device Code Flow, direct tussen uw machine en Microsoft.

## Installatie

1. Zorg dat Node.js geïnstalleerd is.
2. Ga naar deze map:
   ```bash
   cd custom-ms
   npm install  # (optioneel, voor eventuele dependencies, maar script is self-contained)
   ```

## Configuratie (Eenmalig)

Om dit script te gebruiken, moet u een eigen applicatie registreren in Azure (gratis). Dit zorgt dat u de volledige controle heeft over de toegang.

1. Ga naar [Azure Portal > App registrations](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps).
2. Klik op **New registration**.
   - Name: `MyOpenClawIntegratie` (of iets anders)
   - Supported account types: **Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)**.
   - Redirect URI: Laat leeg (niet nodig voor Device Code Flow).
   - Klik **Register**.
3. In het overzicht, kopieer de **Application (client) ID**.
4. Ga in het linkermenu naar **Authentication**.
   - Onder "Advanced settings" > "Allow public client flows", zet "Enable the following mobile and desktop flows" op **Yes**.
   - Klik **Save**.
5. Maak een bestand `config.json` in de `custom-ms` map met de volgende inhoud (vervang `YOUR_CLIENT_ID`):

   ```json
   {
     "clientId": "YOUR_CLIENT_ID_HERE",
     "tenantId": "common"
   }
   ```

## Gebruik

Start het script:

```bash
node index.js
```

1. De eerste keer zal het script een code tonen (bijv. `ABC1234`).
2. Ga naar [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin).
3. Voer de code in.
4. Log in met uw Microsoft account en geef toestemming.
5. Het script pikt automatisch de login op en slaat de tokens veilig op in `tokens.json`.

## Functies

Het script ondersteunt momenteel:
- Recente e-mails lezen
- Agenda-items ophalen
- Contacten inzien
- Bestanden in de root van OneDrive bekijken

## Troubleshooting

- **Token expired**: Verwijder `tokens.json` en log opnieuw in.
- **Geen toegang**: Controleer of de App Registration in Azure de juiste rechten heeft (hoewel `User.Read` etc. standaard dynamisch worden aangevraagd).
