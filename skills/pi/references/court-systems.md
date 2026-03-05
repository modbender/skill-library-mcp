# Florida Court Systems — Quick Reference

## County Clerk Portals (Civil, Criminal, Traffic, Family)

| County | URL | Notes |
|--------|-----|-------|
| Palm Beach | https://applications.mypalmbeachclerk.com/eCaseView/ | JS-rendered, use browser |
| Example County | https://www.example-clerk.org/Web2/CaseSearch/ | Partial web_fetch support |
| Miami-Dade | https://www2.miami-dadeclerk.com/ocs/ | JS-rendered |
| Orange (Orlando) | https://myeclerk.myorangeclerk.com/Cases/Search | JS-rendered |
| Hillsborough (Tampa) | https://pubrec10.hillsclerk.com/ords/f?p=710 | Works with web_fetch sometimes |
| Duval (Jacksonville) | https://core.duvalclerk.com/CoreCms/CaseSearch | JS-rendered |

## Statewide Resources

- **FL Courts directory:** https://www.flcourts.gov/
- **FL Clerk of Courts (all 67 counties):** https://www.flclerks.com/page/FindAClerk
- **FL DOC inmate search:** http://www.dc.state.fl.us/offendersearch/
- **FDLE sex offender search:** https://offender.fdle.state.fl.us/offender/

## Virginia Court Systems

| Court | URL | Notes |
|-------|-----|-------|
| General District | https://eapps.courts.state.va.us/gdcourts/ | Redirect loops, use browser |
| Circuit Court | https://eapps.courts.state.va.us/cjisWeb/ | Better web_fetch support |
| Supreme Court opinions | https://www.vacourts.gov/ | Searchable |

## Federal Courts

| Resource | URL | Cost | Notes |
|----------|-----|------|-------|
| PACER | https://pacer.uscourts.gov | $0.10/pg (free <$30/qtr) | All federal courts |
| PACER Case Locator | https://pcl.uscourts.gov/pcl/ | Free | Cross-court name search |
| CourtListener | https://www.courtlistener.com | Free | RECAP archive + opinions |
| JudyRecords | https://www.judyrecords.com | Free | 760M+ cases, JS-rendered |

## Traffic & Parking (Hard to Find Online)

Most traffic citations and parking tickets are handled at the county clerk level.
They're often in the same system as civil/criminal cases but under "Traffic" case type.

- **FL DHSMV driving record:** https://services.flhsmv.gov/DLCheck/ (requires DL# or full SSN)
- **Parking:** Usually city-level, not county. Check:
  - City of [X] parking violations
  - Municipal court records
  - Red light camera violations (separate system per city)

## Tips

1. Most FL county portals are **JS-rendered** — web_fetch won't work. Use browser tool.
2. Search by **last name first** — many systems want "SMITH, JOHN" format.
3. Traffic cases are often coded as "CT" (County Traffic) or "MO" (Municipal Ordinance).
4. **Expunged/sealed records** won't appear in public searches.
5. **Juvenile records** are always sealed in FL.
6. For historical records (pre-2000), you may need to call the clerk's office directly.
