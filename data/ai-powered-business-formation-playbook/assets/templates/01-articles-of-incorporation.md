# ARTICLES OF INCORPORATION OF {{COMPANY_NAME}}

(Pursuant to NRS Chapter 78)

---

## ARTICLE I — NAME

The name of the corporation is **{{COMPANY_NAME}}** (the "Corporation").

## ARTICLE II — REGISTERED AGENT

The name and street address of the Corporation's registered agent in the State of {{STATE}} is:

**{{REGISTERED_AGENT_NAME}}**
{{REGISTERED_AGENT_STREET}}
{{REGISTERED_AGENT_CITY}}, {{REGISTERED_AGENT_STATE}} {{REGISTERED_AGENT_ZIP}}

## ARTICLE III — PURPOSE

The purpose of the Corporation is to engage in any lawful activity for which corporations may be organized under NRS Chapter 78.

## ARTICLE IV — AUTHORIZED SHARES

The Corporation is authorized to issue the following classes of stock:

{{#EACH STOCK_CLASS}}
### {{CLASS_NAME}}

- **Authorized Shares:** {{AUTHORIZED}}
- **Par Value:** ${{PAR_VALUE}} per share
- **Voting Rights:** {{VOTING_RIGHTS}} vote(s) per share
{{#IF NOTES}}
- **Special Rights:** {{NOTES}}
{{/IF}}
{{/EACH}}

## ARTICLE V — DIRECTORS

The number of directors constituting the initial Board of Directors is {{DIRECTOR_COUNT}}. The names and addresses of the initial directors are:

{{#EACH DIRECTOR}}
- **{{NAME}}** — {{ADDRESS}}
{{/EACH}}

The number of directors may be increased or decreased in accordance with the Bylaws, provided that the number shall not be less than one (1).

## ARTICLE VI — INCORPORATOR

The name and address of the incorporator is:

**{{INCORPORATOR_NAME}}**
{{INCORPORATOR_ADDRESS}}

## ARTICLE VII — INDEMNIFICATION

The Corporation shall indemnify, to the fullest extent permitted by applicable law as it exists on the date hereof or as it may hereafter be amended, any person who was or is a party or is threatened to be made a party to any threatened, pending, or completed action, suit, or proceeding (whether civil, criminal, administrative, or investigative) by reason of the fact that such person is or was a director or officer of the Corporation, or is or was serving at the request of the Corporation as a director, officer, employee, or agent of another corporation, partnership, joint venture, trust, or other enterprise.

## ARTICLE VIII — LIABILITY LIMITATION

To the fullest extent permitted by NRS 78.138, no director or officer of the Corporation shall be personally liable to the Corporation or its stockholders for damages for breach of fiduciary duty as a director or officer, except for liability arising from (i) acts or omissions involving intentional misconduct, fraud, or a knowing violation of law, or (ii) the payment of distributions in violation of NRS 78.300.

## ARTICLE IX — AMENDMENT

The Corporation reserves the right to amend, alter, change, or repeal any provision contained in these Articles of Incorporation in the manner now or hereafter prescribed by statute, and all rights conferred upon stockholders herein are granted subject to this reservation.

---

IN WITNESS WHEREOF, the undersigned incorporator has executed these Articles of Incorporation on this {{FILING_DAY}} day of {{FILING_MONTH}}, {{FILING_YEAR}}.

___________________________
**{{INCORPORATOR_NAME}}**, Incorporator
{{INCORPORATOR_ADDRESS}}
