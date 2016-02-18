# Fio Bank API for Python

[Česky](#Česky)

Python module for easy access to Fio Bank's web API. Uploading payment orders is not implemented yet and I have no plans to work on that for now. But patches are always welcome.

## Overview

- Supported Python Version: 2.7, 3.x
- Module Dependencies: `requests`

This module allows you to query Fio Bank accounts through an instance of `FioBanka` class. First, generate a Fio API token through the internetbanking interface. Then pass the token to `FioBanka` constructor.

According to [official documentation](http://www.fio.cz/docs/cz/API_Bankovnictvi.pdf), it takes up to 5 minutes after generation for the token to become active. The web API also allows only one request per 30 seconds, otherwise you'll get error HTTP 409. `FioBanka` objects honor this restriction and delay consecutive requests as needed. You can bypass the delay by creating fresh `FioBanka` object but you'll only get error instead.

**Important!** The underlying web API is stateful, do not use the same token for access from multiple different systems. Generate unique token for each system instead. If you need to run multiple consecutive `get_*` requests, there will be 30 second delay between them. Use background threads or subprocesses if your application cannot afford such delays.

## Classes and methods

- `FioBanka` - connector class for sending queries to your bank account at Fio Bank.
  - `FioBanka(token)` - constructor, provide token generated through Internet banking interface.
  - `set_last_id(self, transaction_id)` - Manually set starting point for `get_transactions_last()` to the transaction immediately following the given ID. This method triggers neither direct nor indirect delays.
  - `set_last_date(self, date)` - Manually set starting point for `get_transactions_last()` to the first transaction that happened since the beginning of given date. Argument can be `datetime` or `date` object or string in format `YYYY-MM-DD`. This method triggers neither direct nor indirect delays.
  - `get_transactions_last(self)` - Download all new transactions since the last call of this method. You can change the starting point using `set_last_id()` and `set_last_date()` methods. Returns tuple `(_FioTransactionsHeader, [_FioTransaction])`. Causes delay if called less than 30 seconds after previous `get_*` method call.
  - `get_transactions_periods(self, start, end)` - Download all transactions that happened between `start` and `end`. Arguments can be `datetime` or `date` objects or strings in format `YYYY-MM-DD`. Returns tuple `(_FioTransactionsHeader, [_FioTransaction])`. Causes delay if called less than 30 seconds after previous `get_*` method call.
  - `get_report(self, year, report_id, format='pdf')` - Download periodical account report for given `year` and `report_id`. Supported formats are `pdf`, `sta`, `sba_xml` and `cba_xml`. Returns binary string containing report data in requested format. Causes delay if called less than 30 seconds after previous `get_*` method call. **Important!** Do not use the same token for downloading reports in multiple different formats! (Don't ask me why, official documentation says so in section 2.)
- `_FioTransactionsHeader` - Internal class for storing transaction query details.
  - `accountID` - bank account number.
  - `bankID` - four-digit national bank code.
  - `currency` - ISO 4217 currency code for the bank account.
  - `iban` - ISO 13616 international bank account number.
  - `bic` - ISO 9362 bank identification code.
  - `openingBalance` - `decimal` object with account balance before the first transaction in result.
  - `closingBalance` - `decimal` object with account balance after the last transaction in result.
  - `dateStart` - `date` object with starting date of the request.
  - `dateEnd` - `date` object with ending date of the request.
  - `yearList` - account report year.
  - `idList` - account report ID.
  - `idFrom` - ID of the first transaction in result.
  - `idTo` - ID of the last transaction in result.
  - `idLastDownload` - ID of transaction immediately preceding the first one in result.
- `_FioTransaction` - Internal class for storing transaction details.
  - `id` - unique transaction ID.
  - `date` - `date` object with date when the transaction happened.
  - `amount` - `decimal` object with amount of money transfered in this transaction.
  - `currency` - ISO 4217 currency code for this transaction.
  - `remote_account` - remote account number.
  - `remote_account_name` - remote account name.
  - `bank_id` - four-digit national bank code for the remote account.
  - `bank_name` - bank name for the remote account.
  - `constant_symbol` - processing information for recipient. Up to 4 digits with leading zeros stored as string.
  - `variable_symbol` - processing information for recipient. Up to 10 digits with leading zeros stored as string.
  - `specific_symbol` - processing information for recipient. Up to 10 digits with leading zeros stored as string.
  - `user_identity` - user identity.
  - `type` - description of transfer in Czech.
  - `authorized_by` - user who authorized the order.
  - `message` - arbitrary message for recipient.
  - `comment` - comment.
  - `order_id` - ID of payment order. Single order may create multiple transactions (e.g. for fees or even inverse transactions for cancelled orders).

# Česky

Python modul pro snadný přístup k výpisům z účtu přes webové API Fio Banky. Odesílání platebních příkazů zatím není implementované a ani se na něm zatím nechystám pracovat. Patche ale uvítám.

## Přehled

- Podporované verze Pythonu: 2.7, 3.x
- Vyžadované moduly: `requests`

Tento modul umožňuje číst informace z bankovních účtů u Fio banky prostřednictvím instance třídy `FioBanka`. Nejprve si přes internetové bankovnictví vygenerujte přístupový token. Pak ten token zadejte jako parametr konstruktoru třídy `FioBanka`.

Podle [oficiální dokumentace](http://www.fio.cz/docs/cz/API_Bankovnictvi.pdf) může trvat až 5 minut, než se token po vygenerování aktivuje. Webové API dále povoluje jen jeden dotaz za 30 sekund, jinak vrátí chybu HTTP 409. Třída `FioBanka` proto mezi vícenásobné dotazy podle potřeby vkládá dostatečnou časovou prodlevu. Tuto prodlevu sice můžete obejít vytvořením nové instance třídy `FioBanka`, ale pak dostanete jen chybu.

**Pozor!** API na serveru Fio banky si udržuje interní stav, takže nepoužívejte stejný token pro přístup z několika různých systémů. Pro každý systém si vygenerujte token zvlášť. Pokud budete volat několik `get_*` dotazů za sebou, jejich zpracování může trvat až 30 sekund. Pokud si váš program nemůže dovolit tak dlouho čekat, použijte vlákna nebo podprocesy.

## Třídy a metody

- `FioBanka` - třída pro připojení k účtu u Fio banky a odesílání dotazů.
  - `FioBanka(token)` - konstruktor, zadejte token vygenerovaný přes internetové bankovnictví.
  - `set_last_id(self, transaction_id)` - ruční nastavení počátečního bodu pro `get_transactions_last()` na záznam, který bezprostředně následuje po pohybu se zadaným ID. Tato metoda nezpůsobuje přímé ani nepřímé prodlevy.
  - `set_last_date(self, date)` - ruční nastavení počátečního bodu pro `get_transactions_last()` na první záznam od začátku zadaného data. Argument může být `datetime` nebo `date` objekt nebo řetězec ve formátu `YYYY-MM-DD`. Tato metoda nezpůsobuje přímé ani nepřímé prodlevy.
  - `get_transactions_last(self)` - stáhne všechny nové pohyby na účtu od posledního volání této metody. Počáteční bod můžete změnit ručně pomocí metod `set_last_id()` a `set_last_date()`. Vrací tuple `(_FioTransactionsHeader, [_FioTransaction])`. Když tuto metodu zavoláte dříve než 30 sekund po předchozím volání kterékoliv `get_*` metody, vynutí se časová prodleva.
  - `get_transactions_periods(self, start, end)` - stáhne všechny pohyby na účtu mezi daty `start` a `end`. Argumenty mohou být `datetime` nebo `date` objekty nebo řetězce ve formátu `YYYY-MM-DD`. Vrací tuple `(_FioTransactionsHeader, [_FioTransaction])`. Když tuto metodu zavoláte dříve než 30 sekund po předchozím volání kterékoliv `get_*` metody, vynutí se časová prodleva.
  - `get_report(self, year, report_id, format='pdf')` - stáhne výpis z účtu pro zadaný rok `year` a číslo výpisu `report_id`. Podporované formáty jsou `pdf`, `sta`, `sba_xml` a `cba_xml`. Vrací binární řetězec obsahující data výpisu z účtu v požadovaném formátu. Když tuto metodu zavoláte dříve než 30 sekund po předchozím volání kterékoliv `get_*` metody, vynutí se časová prodleva. **Pozor!** Nepoužívejte stejný token pro stahování výpisů v několika různých formátech! (Neptejte se mě proč, píše se to v sekci 2 oficiální dokumentace.)
- `_FioTransactionsHeader` - interní třída pro ukládání podrobností o dotazu na pohyby na účtu.
  - `accountID` - číslo bankovního účtu.
  - `bankID` - čtyřciferný kód banky.
  - `currency` - kód měny účtu podle ISO 4217.
  - `iban` - mezinárodní číslo účtu podle ISO 13616.
  - `bic` - mezinárodní kód banky podle ISO 9362.
  - `openingBalance` - `decimal` objekt s počátečním zůstatkem na účtu v daném období.
  - `closingBalance` - `decimal` objekt s koncovým zůstatkem na účtu v daném období.
  - `dateStart` - `date` objekt s počátečním datem období.
  - `dateEnd` - `date` objekt s koncovým datem období.
  - `yearList` - rok zvoleného výpisu.
  - `idList` - číslo zvoleného výpisu.
  - `idFrom` - ID prvního pohybu na účtu v daném období.
  - `idTo` - ID posledního pohybu na účtu v daném období.
  - `idLastDownload` - ID pohybu na účtu, který bezprostředně předchází prvnímu pohybu vrácenému tímto dotazem.
- `_FioTransaction` - interní třída pro ukládání podrobností o jednom pohybu na účtu.
  - `id` - unikátní ID pohybu.
  - `date` - `date` objekt obsahující datum, kdy se pohyb uskutečnil.
  - `amount` - `decimal` objekt s přijatou/odeslanou částkou.
  - `currency` - kód měny přijaté/odeslané částky podle ISO 4217.
  - `remote_account` - číslo protiúčtu.
  - `remote_account_name` - název protiúčtu.
  - `bank_id` - čtyřciferný kód banky protiúčtu.
  - `bank_name` - název banky protiúčtu.
  - `constant_symbol` - konstantní symbol, až čtyřmístné číslo uložené jako řetězec včetně počátečních nul.
  - `variable_symbol` - variabilní symbol, až desetimístné číslo uložené jako řetězec včetně počátečních nul.
  - `specific_symbol` - specifický symbol, až desetimístné číslo uložené jako řetězec včetně počátečních nul.
  - `user_identity` - uživatelská identifikace.
  - `type` - popis typu pohybu.
  - `authorized_by` - oprávněná osoba, která zadala příkaz.
  - `message` - zpráva pro příjemce.
  - `comment` - komentář.
  - `order_id` - ID platebního příkazu. Jeden platební příkaz může vygenerovat několik různých pohybů (např. poplatky, ale i inverzní pohyby v případě zrušení platby).
