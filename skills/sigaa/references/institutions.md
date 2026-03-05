# SIGAA - Institutions and Login URLs

SIGAA was developed by UFRN (Universidade Federal do Rio Grande do Norte) and is used by 50+ Brazilian federal universities and institutes.

## Login URL Patterns

| Institution | SIGAA Base URL | CAS/Login URL | Notes |
|-------------|---------------|----------------|-------|
| UNB | https://sigaa.unb.br | https://autenticacao.unb.br/sso-server | Uses CAS SSO; username = matricula number (e.g. 241104251) |
| UFRN | https://sigaa.ufrn.br | https://sigaa.ufrn.br/sigaa/verTelaLogin.do | Direct login |
| UFC | https://si3.ufc.br | https://si3.ufc.br/sigaa/verTelaLogin.do | Direct login |
| UFPE | https://sigaa.ufpe.br | https://sigaa.ufpe.br/sigaa/verTelaLogin.do | Direct login |
| UFCG | https://sigaa.ufcg.edu.br | https://sigaa.ufcg.edu.br/sigaa/verTelaLogin.do | Direct login |
| UFPI | https://sigaa.ufpi.br | https://sigaa.ufpi.br/sigaa/verTelaLogin.do | Direct login |
| UFRRJ | https://sigaa.ufrrj.br | https://sigaa.ufrrj.br/sigaa/verTelaLogin.do | Direct login |
| UFSB | https://sigaa.ufsb.edu.br | https://sigaa.ufsb.edu.br/sigaa/verTelaLogin.do | Direct login |
| UFSJ | https://www.sig.ufsj.edu.br | https://www.sig.ufsj.edu.br/sigaa/verTelaLogin.do | Direct login |
| UFPA | https://sigaa.ufpa.br | https://sigaa.ufpa.br/sigaa/verTelaLogin.do | Direct login |
| UFPB | https://sigaa.ufpb.br | https://sigaa.ufpb.br/sigaa/verTelaLogin.do | Direct login |
| UFBA | https://sigaa.ufba.br | https://sigaa.ufba.br/sigaa/verTelaLogin.do | Direct login |
| UFRB | https://sigaa.ufrb.edu.br | https://sigaa.ufrb.edu.br/sigaa/verTelaLogin.do | Direct login |
| IFFarroupilha | https://sig.iffarroupilha.edu.br | — | Instituto Federal |

## Username Formats by Institution

- **UNB**: Matricula number (e.g. `241104251`) — NOT the CPF
- **UFRN**: Usually CPF or login SIAPE (for professors)
- **Most others**: CPF without dots/dashes OR institution registration number

## Authentication Methods

### CAS SSO (UNB and some institutions)
1. GET `https://<cas-server>/sso-server/login?service=https://<sigaa-url>/sigaa/login/cas`
2. Extract: `lt` token, `execution` token, form `action` URL, session cookie
3. POST to form action with: `username`, `password`, `lt`, `execution`, `_eventId=submit`
4. Follow redirect back to SIGAA (receives SIGAA JSESSIONID)

### Direct Login (most institutions)
1. GET `https://<sigaa>/sigaa/verTelaLogin.do`
2. Extract: `javax.faces.ViewState`, session cookie
3. POST to `/sigaa/logar.do` with: `dispatch=logOn`, `user.login`, `user.senha`, `javax.faces.ViewState`

## Portal URLs

| Portal | URL path |
|--------|----------|
| Discente | `/sigaa/portais/discente/discente.jsf` |
| Docente | `/sigaa/verPortalDocente.do` |
| Public | `/sigaa/public/home.jsf` |
| All Classes (turmas) | `/sigaa/portais/discente/turmas.jsf` |
